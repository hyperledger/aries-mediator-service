import app from './app';
import logger from './logger';

const port = app.get('port');
const server = app.listen(port);

process.on('unhandledRejection', (reason, p) =>
  logger.error('Unhandled Rejection at: Promise ', p, reason)
);

process.on('SIGTERM', () => {
  logger.warn('SIGTERM received, closing server.');
  server.close(() => {
    logger.warn('Server closed, exiting.');
    process.exit(0);
  });
});

server.on('listening', () =>
  logger.info(
    'Feathers application started on http://%s:%d',
    app.get('host'),
    port
  )
);
