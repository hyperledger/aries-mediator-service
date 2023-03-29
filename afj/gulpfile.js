const gulp = require('gulp');
const clean = require('gulp-clean');
const ts = require('gulp-typescript');
const { exec } = require('child_process');
const tsp = ts.createProject('tsconfig.json');
const sourcemaps = require('gulp-sourcemaps');
const child = require('child_process');

gulp.task('clean', () =>
  gulp.src('dist', { read: false, allowEmpty: true }).pipe(
    clean({
      force: true,
    }),
  ),
);

gulp.task('transpile-src', () =>
  tsp
    .src()
    .pipe(sourcemaps.init())
    .pipe(tsp())
    .js.pipe(
      sourcemaps.write('.', {
        includeContent: false,
        sourceRoot: (file) => {
          return file.cwd + '/src';
        },
      }),
    )
    .pipe(gulp.dest('dist/src')),
);

// gulp.task('copy-app-config', () =>
//   gulp.src('src/config/*.json').pipe(gulp.dest('dist/src/config')),
// );

// gulp.task('copy-files', () =>
//   gulp
//     .src(['package.json', 'package-lock.json', 'Dockerfile'])
//     .pipe(gulp.dest('dist')),
// );



// // Change CMD to `npm start`
// // gulp.task('update-docker-cmd', cb =>
// //   exec('sed -i.orig-1 -e s/\\"run\\"\\,\\ \\"dev\\"/\\"start\\"/ ./dist/Dockerfile', err =>
// //     cb(err),
// //   ),
// // );

// gulp.task('copy-public', () =>
//   gulp.src('public/**').pipe(gulp.dest('dist/public')),
// );

// gulp.task('copy-env', () =>
//   child.spawn('cp', ['-a', '../devops/.env', './dist/'], { stdio: 'inherit' }),
// );

// gulp.task('copy-node_modules', () =>
//   gulp.src('node_modules/**').pipe(gulp.dest('dist/node_modules')),
// );

gulp.task(
  'default',
  gulp.series(
    'clean',
    // 'build-api-doc',
    gulp.parallel(
      'transpile-src',
      // 'copy-app-config',
      // 'copy-public',
      // 'copy-files',
      // 'copy-node_modules',
    ),
  ),
);

// gulp.task('watch-src-changes', () =>
//   gulp.watch(
//     ['src/**/*.{ts}'],
//     gulp.parallel(
//       'transpile-src',
//       'copy-node-config',
//       'copy-env',
//     ),
//   ),
// );
