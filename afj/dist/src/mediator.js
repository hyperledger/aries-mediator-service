"use strict";
/**
 * This file contains a sample mediator. The mediator supports both
 * HTTP and WebSockets for communication and will automatically accept
 * incoming mediation requests.
 *
 * You can get an invitation by going to '/invitation', which by default is
 * http://localhost:3001/invitation
 *
 * To connect to the mediator from another agent, you can set the
 * 'mediatorConnectionsInvite' parameter in the agent config to the
 * url that is returned by the '/invitation/ endpoint. This will connect
 * to the mediator, request mediation and set the mediator as default.
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
var _a, _b;
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@aries-framework/core");
const express_1 = __importDefault(require("express"));
const ws_1 = require("ws");
const core_2 = require("@aries-framework/core");
const node_1 = require("@aries-framework/node");
const port = process.env.AGENT_PORT ? Number(process.env.AGENT_PORT) : 3001;
// We create our own instance of express here. This is not required
// but allows use to use the same server (and port) for both WebSockets and HTTP
const app = (0, express_1.default)();
const socketServer = new ws_1.Server({ noServer: true });
const endpoints = (_b = (_a = process.env.AGENT_ENDPOINTS) === null || _a === void 0 ? void 0 : _a.split(",")) !== null && _b !== void 0 ? _b : [
    `http://localhost:${port}`,
    `ws://localhost:${port}`,
];
const agentConfig = {
    endpoints,
    label: process.env.AGENT_LABEL || "Aries Framework JavaScript Mediator",
    walletConfig: {
        id: process.env.WALLET_NAME || "AriesFrameworkJavaScript",
        key: process.env.WALLET_KEY || "AriesFrameworkJavaScript",
    },
    autoAcceptConnections: true,
    autoAcceptMediationRequests: true,
    logger: new core_1.ConsoleLogger(core_1.LogLevel.debug),
};
// Set up agent
const agent = new core_2.Agent({
    config: agentConfig,
    dependencies: node_1.agentDependencies,
});
const config = agent.config;
// Create all transports
const httpInboundTransport = new node_1.HttpInboundTransport({ app, port });
const httpOutboundTransport = new core_2.HttpOutboundTransport();
const wsInboundTransport = new node_1.WsInboundTransport({ server: socketServer });
const wsOutboundTransport = new core_2.WsOutboundTransport();
// Register all Transports
agent.registerInboundTransport(httpInboundTransport);
agent.registerOutboundTransport(httpOutboundTransport);
agent.registerInboundTransport(wsInboundTransport);
agent.registerOutboundTransport(wsOutboundTransport);
// Allow to create invitation, no other way to ask for invitation yet
httpInboundTransport.app.get("/invitation", async (req, res) => {
    if (typeof req.query.c_i === "string") {
        const invitation = core_2.ConnectionInvitationMessage.fromUrl(req.url);
        res.send(invitation.toJSON());
    }
    else {
        const { outOfBandInvitation } = await agent.oob.createInvitation();
        const httpEndpoint = config.endpoints.find((e) => e.startsWith("http"));
        res.send(outOfBandInvitation.toUrl({ domain: httpEndpoint + "/invitation" }));
    }
});
const main = async () => {
    var _a;
    await agent.initialize();
    // When an 'upgrade' to WS is made on our http server, we forward the
    // request to the WS server
    (_a = httpInboundTransport.server) === null || _a === void 0 ? void 0 : _a.on("upgrade", (request, socket, head) => {
        socketServer.handleUpgrade(request, socket, head, (socket) => {
            socketServer.emit("connection", socket, request);
        });
    });
};
main();

//# sourceMappingURL=mediator.js.map
