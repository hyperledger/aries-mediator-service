export enum ServiceType {
  Connection = 'Connection',
}

export enum WebhookTopic {
  Connections = 'connections',
}

export enum ConnectionState {
  InvitationSent = 'invitation-sent',
  Request = 'request',
  Response = 'response',
  Active = 'active',
  Completed = 'completed',
}

export enum ConnectionServiceAction {
  Accept_Connection_Request = 'Accept-Request',
  Send_Connection_Ping = 'Send-Ping'
}
