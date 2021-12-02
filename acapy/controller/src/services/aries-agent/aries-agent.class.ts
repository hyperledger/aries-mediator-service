import { NotImplemented } from '@feathersjs/errors';
import { Params } from '@feathersjs/feathers';
import Axios, { AxiosError } from 'axios';
import { Application } from '../../declarations';
import logger from '../../logger';
import { EndorserServiceAction, ServiceType } from '../../models/enums';
import { AriesAgentError } from '../../models/errors';
import { AcaPyUtils } from '../../utils/aca-py';

export interface AriesAgentData {
  service: ServiceType;
  action: EndorserServiceAction;
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
      case ServiceType.Endorser:
        if (data.action === EndorserServiceAction.Set_Metadata) {
          return this.setEndorserRole(data.data.connection_id);
        } else if (data.action === EndorserServiceAction.Endorse_Transaction) {
          return this.endorseTransaction(data.data.transaction_id);
        }
      default:
        return new NotImplemented(
          `The operation ${data.service}/${data.action} is not supported`
        );
    }
  }

  private async setEndorserRole(connection_id: string): Promise<boolean> {
    try {
      const endorserRole = 'TRANSACTION_ENDORSER';
      const url = `${this.acaPyUtils.getAdminUrl()}/transactions/${connection_id}/set-endorser-role`;
      logger.debug(
        `Setting role metadata for connection with id ${connection_id}`
      );
      const response = await Axios.post(
        url,
        {},
        {
          ...this.acaPyUtils.getRequestConfig(),
          ...{ params: { transaction_my_job: endorserRole } },
        }
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

  private async endorseTransaction(transaction_id: string): Promise<boolean> {
    try {
      logger.debug(
        `Endorse transaction with id ${transaction_id}`
      );

      const url = `${this.acaPyUtils.getAdminUrl()}/transactions/${transaction_id}/endorse`;

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
