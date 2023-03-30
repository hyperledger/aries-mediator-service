
var ariesCore = require('@aries-framework/core')
var ariesNode = require('@aries-framework/node')

var config = require('./config.js')

var deferred = require('deferred')
var process = require('process')

const characters ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

function generateString(length) {
    let result = ' ';
    const charactersLength = characters.length;
    for ( let i = 0; i < length; i++ ) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }

    return result;
}

const initializeAgent = async (withMediation, port) => {
    // Simple agent configuration. This sets some basic fields like the wallet
    // configuration and the label. It also sets the mediator invitation url,
    // because this is most likely required in a mobile environment.

    let mediation_url = config.mediation_url;
    let endpoints = ['http://'+ config.agent_ip + ':' + port] 

    const agentConfig = {
        indyLedgers: [config.ledger],
        label: generateString(14),
        walletConfig: {
            id: generateString(32),
            key: generateString(32),
        },
        autoAcceptConnections: true,
        endpoints: endpoints,

        autoAcceptInvitation: true,
        // logger: new ariesCore.ConsoleLogger(ariesCore.LogLevel.trace),
        mediatorConnectionsInvite: mediation_url,
    }

    if (withMediation) {
        delete agentConfig['endpoints']
    } else {
        delete agentConfig['mediatorConnectionsInvite']
    }

    // A new instance of an agent is created here
    const agent = new ariesCore.Agent({
            config: agentConfig, 
            dependencies: ariesNode.agentDependencies
        })

    // Register a simple `WebSocket` outbound transport
    agent.registerOutboundTransport(new ariesCore.WsOutboundTransport())

    // Register a simple `Http` outbound transport
    agent.registerOutboundTransport(new ariesCore.HttpOutboundTransport())


    if (withMediation) {

        // wait for medation to be configured
        let timeout = 2 * 60000 ;// two minutes 

        const TimeDelay = new Promise((resolve, reject) => {
            setTimeout(resolve, timeout, false)
        })

        var def = deferred()

        var onConnectedMediation = async (event)=>{
            const mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection()
            if(event.payload.connectionId === mediatorConnection?.id){
                def.resolve(true)
                // we no longer need to listen to the event
                agent.events.off(ariesCore.TransportEventTypes.OutboundWebSocketOpenedEvent, onConnectedMediation);
            }
        }

        agent.events.on(ariesCore.TransportEventTypes.OutboundWebSocketOpenedEvent, onConnectedMediation)

        // Initialize the agent
        await agent.initialize()

        // wait for ws to be configured
        value = await Promise.race([TimeDelay, def.promise])

        if (!value) {
            // we no longer need to listen to the event in case of failure
            agent.events.off(ariesCore.TransportEventTypes.OutboundWebSocketOpenedEvent, onConnectedMediation);
            throw 'Mediator timeout!';
        }
    } else {
        agent.registerInboundTransport(new ariesNode.HttpInboundTransport({ port: port }))
        await agent.initialize()
    }

    return agent
}

const pingMediator = async(agent) => {
    // Find mediator

    // wait for the ping
    let timeout = 2 * 60000 ;// two minutes 

    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false)
    })

    var def = deferred()

    var onPingResponse = async (event)=>{
        const mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection()
        if(event.payload.connectionRecord.id === mediatorConnection?.id){
            // we no longer need to listen to the event
            agent.events.off(ariesCore.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);

            def.resolve(true)
        }

    }

    agent.events.on(ariesCore.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);

    let mediatorConnection = await agent.mediationRecipient.findDefaultMediatorConnection()

    if(mediatorConnection){
        //await agent.connections.acceptResponse(mediatorConnection.id)
        await agent.connections.sendPing(mediatorConnection.id, {})
    }

    // wait for ping repsonse
    value = await Promise.race([TimeDelay, def.promise])

    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(ariesCore.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);
        throw 'Mediator timeout!';
    }
}

let receiveInvitation = async(agent, invitationUrl) => {

    // wait for the connection
    let timeout = 2 * 60000 ;// two minutes 

    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false)
    })

    var def = deferred()

    var onConnection = async (event) => {
        {
            let payload = event.payload
            if (payload.connectionRecord.state === ariesCore.DidExchangeState.Completed) {
                // the connection is now ready for usage in other protocols!
                // console.log(`Connection for out-of-band id ${payload.connectionRecord.outOfBandId} completed`)
                // Custom business logic can be included here
                // In this example we can send a basic message to the connection, but
                // anything is possible

                agent.events.off(ariesCore.ConnectionEventTypes.ConnectionStateChanged, onConnection);

                def.resolve(true)
            }
        }
    }

    agent.events.on(ariesCore.ConnectionEventTypes.ConnectionStateChanged, onConnection)

    const { outOfBandRecord } = await agent.oob.receiveInvitationFromUrl(invitationUrl)

    // wait for connection
    value = await Promise.race([TimeDelay, def.promise])

    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(ariesCore.ConnectionEventTypes.ConnectionStateChanged, onConnection);
        throw 'Connection timeout!';
    }

    return outOfBandRecord
}

let receiveCredential = async (agent) => {
    // wait for the ping
    let timeout = 2 * 60000 ;// two minutes 

    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false)
    })

    var def = deferred()

    let onCredential = async (event) => {
        let payload = event.payload

        switch (payload.credentialRecord.state) {
            case ariesCore.CredentialState.OfferReceived:
            //console.log('received a credential')
            // custom logic here
            await agent.credentials.acceptOffer({ credentialRecordId: payload.credentialRecord.id })
            case ariesCore.CredentialState.Done:
            //console.log(`Credential for credential id ${payload.credentialRecord.id} is accepted`)
            // For demo purposes we exit the program here.

            agent.events.off(ariesCore.CredentialEventTypes.CredentialStateChanged, onCredential);

            def.resolve(true)
        }
    }

    agent.events.on(ariesCore.CredentialEventTypes.CredentialStateChanged, onCredential)

    // Nothing for us to do

    // wait for credential
    value = await Promise.race([TimeDelay, def.promise])

    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(ariesCore.CredentialEventTypes.CredentialStateChanged, onCredential);
        throw 'Credential timeout!';
    }
}

let receiveMessage = async(agent) => {
    // wait for the ping
    let timeout = 2 * 60000 ;// two minutes 

    const TimeDelay = new Promise((resolve, reject) => {
        setTimeout(resolve, timeout, false)
    })

    var def = deferred()

    let onMessage = async (event) => {
        let payload = event.payload

//        console.error(payload)

        agent.events.off(ariesCore.BasicMessageEventTypes.BasicMessageStateChanged, onMessage);

        def.resolve(true)
    }

    agent.events.on(ariesCore.BasicMessageEventTypes.BasicMessageStateChanged, onMessage)

    // Nothing for us to do

    // wait for credential
    value = await Promise.race([TimeDelay, def.promise])

    if (!value) {
        // we no longer need to listen to the event in case of failure
        agent.events.off(ariesCore.BasicMessageEventTypes.BasicMessageStateChanged, onMessage);
        throw 'Message timeout!';
    } 
}

var readline = require('readline');
const { ConsoleLogger } = require('@aries-framework/core')

var rl = readline.createInterface(
    process.stdin, null);

var agent = null;

rl.setPrompt("");
rl.prompt(false)


const handleError = async (e) => {
    process.stdout.write(JSON.stringify({'error':1, 'result': e}) + "\n")
}

rl.on('line', async (line) => {
    try {
        var command = JSON.parse(line)

        if ( command['cmd'] == 'start' && agent == null) {
        
            agent = await initializeAgent(command['withMediation'], command['port'])
            process.stdout.write(JSON.stringify({'error':0, 'result': 'Initialized agent...'}) + "\n")
        
        } else if ( command['cmd'] == 'ping_mediator') {
            await pingMediator(agent)

            process.stdout.write(JSON.stringify({'error':0, 'result': 'Ping Mediator'}) + "\n")
        } else if ( command['cmd'] =='receiveInvitation') {
            let connection = await receiveInvitation(agent, command['invitationUrl'])

            process.stdout.write(JSON.stringify({'error':0, 'result': 'Receive Connection', "connection": connection}) + "\n")
        } else if ( command['cmd'] =='receiveCredential') {
            await receiveCredential(agent)

            process.stdout.write(JSON.stringify({'error':0, 'result': 'Receive Credential'}) + "\n")
        } else if ( command['cmd'] == 'receiveMessage') {
            await receiveMessage(agent)

            process.stdout.write(JSON.stringify({'error':0, 'result': 'Receive Message'}) + "\n")
        } else if ( command['cmd'] =='shutdown') {
            process.stdout.write(JSON.stringify({'error':0, 'result': 'Shutting down agent'}) + "\n")
            rl.close();
            await agent.shutdown();
            process.exit(1);
        } else {
            handleError('invalid command')
        }
    } catch (e) {
        handleError(e)
    }
});

process.once('SIGTERM', function (code) {
    process.stderr.write('SIGTERM received...' + "\n");
    process.exit(1);
});

// Is there a better way to handle this. 
// TODO it is recommended to shutdown the agent after an error like this...
process
  .on('unhandledRejection', (reason, p) => {
    handleError(reason);
    process.exit(1);
  })
  .on('uncaughtException', err => {
    handleError(err);
    process.exit(1);
  });
  
