import { FeathersError } from '@feathersjs/errors';

export class UndefinedAppError extends Error {}

export class DuplicatedProfileError extends Error {}

export class AriesAgentError extends FeathersError {
  constructor(message: string | Error, code: number | undefined, data?: unknown) {
    super(message, 'aries-agent-error', code || 500, 'AriesAgentError', data);
  }
}
