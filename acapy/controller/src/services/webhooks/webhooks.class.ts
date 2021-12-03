import { NotImplemented } from '@feathersjs/errors';
import { Params, ServiceMethods } from '@feathersjs/feathers';
import { Application } from '../../declarations';
import {
  ConnectionState,
  ConnectionServiceAction,
  ServiceType,
  WebhookTopic
} from '../../models/enums';
import { AriesAgentData } from '../aries-agent/aries-agent.class';

interface Data {
  state: ConnectionState;
  connection_id?: string;
  transaction_id?: string;
}

interface ServiceOptions {}

export class Webhooks implements Partial<ServiceMethods<Data>> {
  app: Application;
  options: ServiceOptions;

  constructor(options: ServiceOptions = {}, app: Application) {
    this.options = options;
    this.app = app;
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async create(data: Data, params?: Params): Promise<any> {
    const topic = params?.route?.topic;
    const state = data?.state;
    console.log("Received webhook:", topic, state);
    switch (topic) {
      case WebhookTopic.Connections:
        if (state === ConnectionState.Request) {
          // auto-accept connection requests
          await this.app.service('aries-agent').create({
            service: ServiceType.Connection,
            action: ConnectionServiceAction.Accept_Connection_Request,
            data: {
              connection_id: data.connection_id,
            },
          } as AriesAgentData);
        } else if (state === ConnectionState.Response) {
          // auto-ping completes connections
          await this.app.service('aries-agent').create({
            service: ServiceType.Connection,
            action: ConnectionServiceAction.Send_Connection_Ping,
            data: {
              connection_id: data.connection_id,
            },
          } as AriesAgentData);
        } else if (state === ConnectionState.Completed) {
          // No-op I think ...
        }
        return { result: 'Success' };
      default:
        return new NotImplemented(`Webhook ${topic} is not supported`);
    }
  }
}
