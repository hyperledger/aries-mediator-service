export enum ServiceType {
  Endorser = 'Endorser',
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

export enum EndorserServiceAction {
  Endorse_Transaction = 'Endorse',
  Set_Metadata = 'Metadata'
}

export enum EndorserTopic {
  EndorseTransaction = 'endorse_transaction'
}

export enum EndorserState {
  RequestReceived = 'request_received'
}