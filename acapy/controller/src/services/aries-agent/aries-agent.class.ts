import { NotImplemented } from '@feathersjs/errors';
import { Params } from '@feathersjs/feathers';
import Axios, { AxiosError } from 'axios';
import { Application } from '../../declarations';
import logger from '../../logger';
import { ConnectionServiceAction, ServiceType } from '../../models/enums';
import { AriesAgentError } from '../../models/errors';
import { AcaPyUtils } from '../../utils/aca-py';

export interface AriesAgentData {
  service: ServiceType;
  action: ConnectionServiceAction;
  data: any;
}

interface ServiceOptions {}

export class AriesAgent {
  app: Application;
  options: ServiceOptions;
  acaPyUtils: AcaPyUtils;

  constructor(options: ServiceOptions = {}, app: Application) {
    this.options = options;
    this.app = app;
    this.acaPyUtils = AcaPyUtils.getInstance(app);
    this.init();
  }

  private async init() {
    await this.acaPyUtils.init();
    logger.info('Aries Agent service initialized');
  }

  //eslint-disable-next-line @typescript-eslint/no-unused-vars
  async create(data: AriesAgentData, params?: Params): Promise<any> {
    switch (data.service) {
      case ServiceType.Connection:
        if (data.action === ConnectionServiceAction.Accept_Connection_Request) {
          return this.acceptConnectionRequest(data.data.connection_id);
        } else if (data.action === ConnectionServiceAction.Send_Connection_Ping) {
          return this.sendConnectionPing(data.data.connection_id);
        }
      default:
        return new NotImplemented(
          `The operation ${data.service}/${data.action} is not supported`
        );
    }
  }

  private async acceptConnectionRequest(connection_id: string): Promise<boolean> {
    try {
      const url = `${this.acaPyUtils.getAdminUrl()}/connections/${connection_id}/accept-request`;
      logger.debug(
        `Accept connection request for connection with id ${connection_id}`
      );
      const response = await Axios.post(
        url,
        {},
        this.acaPyUtils.getRequestConfig()
      );
      return response.status === 200 ? true : false;
    } catch (e) {
      const error = e as AxiosError;
      throw new AriesAgentError(
        error.response?.statusText || error.message,
        error.response?.status,
        error.response?.data
      );
    }
  }

  private async sendConnectionPing(connection_id: string): Promise<boolean> {
    try {
      logger.debug(
        `Ping connection with id ${connection_id}`
      );

      const url = `${this.acaPyUtils.getAdminUrl()}/connections/${connection_id}/send-ping`;

      const response = await Axios.post(
        url,
        {},
        this.acaPyUtils.getRequestConfig()
      );
      return response.status === 200 ? true : false;
    } catch (e) {
      const error = e as AxiosError;
      throw new AriesAgentError(
        error.response?.statusText || error.message,
        error.response?.status,
        error.response?.data
      );
    }
  }
}
