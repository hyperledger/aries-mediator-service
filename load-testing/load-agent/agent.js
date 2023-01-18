
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

const initializeAgent = async () => {
    // Simple agent configuration. This sets some basic fields like the wallet
    // configuration and the label. It also sets the mediator invitation url,
    // because this is most likely required in a mobile environment.

    const agentConfig = {
        label: generateString(14),
        walletConfig: {
            id: generateString(32),
            key: generateString(32),
        },
        autoAcceptConnections: true,
        // endpoints: ['http://localhost:3002'],

        // autoAcceptInvitation: true,
        // logger: new ariesCore.ConsoleLogger(ariesCore.LogLevel.trace),
        mediatorConnectionsInvite: config.mediation_url,
    }

    // A new instance of an agent is created here
    const agent = new ariesCore.Agent(
        {
            config: agentConfig, 
            dependencies: ariesNode.agentDependencies}
        )

    // Register a simple `WebSocket` outbound transport
    agent.registerOutboundTransport(new ariesCore.WsOutboundTransport())

    // Register a simple `Http` outbound transport
    agent.registerOutboundTransport(new ariesCore.HttpOutboundTransport())

    // agent.registerInboundTransport(new ariesNode.HttpInboundTransport({ port: 3002 }))

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
            def.resolve(true)
            // we no longer need to listen to the event
            agent.events.off(ariesCore.TrustPingEventTypes.TrustPingResponseReceivedEvent, onPingResponse);
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

var readline = require('readline');

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
        
            agent = await initializeAgent()
            process.stdout.write(JSON.stringify({'error':0, 'result': 'Initialized agent...'}) + "\n")
        
        } else if ( command['cmd'] == 'ping_mediator') {
            await pingMediator(agent)

            process.stdout.write(JSON.stringify({'error':0, 'result': 'Ping Mediator'}) + "\n")
        } else if ( command['cmd'] =='shutdown') {
            process.stdout.write(JSON.stringify({'error':0, 'result': 'Shutting down agent'}) + "\n")
            rl.close();
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
  })
  .on('uncaughtException', err => {
    handleError(err);
    process.exit(1);
  });