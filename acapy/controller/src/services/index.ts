import { Application } from '../declarations';
import ariesAgent from './aries-agent/aries-agent.service';
import webhooks from './webhooks/webhooks.service';
// Don't remove this comment. It's needed to format import lines nicely.

export default function (app: Application): void {
  app.configure(ariesAgent);
  app.configure(webhooks);
}
