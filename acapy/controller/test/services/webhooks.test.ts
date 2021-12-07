import app from '../../src/app';

describe('\'webhooks\' service', () => {
  it('registered the service', () => {
    const service = app.service('webhooks/topic/:topic');
    expect(service).toBeTruthy();
  });
});
