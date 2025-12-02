import { execSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const distDir = path.join(__dirname, 'dist');
const repoUrl = 'https://github.com/AyushShahi01/Mahalaxmi-tours-and-travels.git';

console.log('Starting manual deployment...');

try {
  if (!fs.existsSync(distDir)) {
    throw new Error('dist directory not found. Run npm run build first.');
  }

  process.chdir(distDir);
  console.log('Changed directory to dist');

  // Initialize git if not exists
  if (!fs.existsSync(path.join(distDir, '.git'))) {
    execSync('git init');
    console.log('Initialized git repository');
    execSync('git checkout -b gh-pages');
    console.log('Created gh-pages branch');
  } else {
      // If it exists, ensure we are on gh-pages
      try {
        execSync('git checkout gh-pages');
      } catch (e) {
        execSync('git checkout -b gh-pages');
      }
  }

  execSync('git add -A');
  console.log('Added files');

  try {
    execSync('git commit -m "Deploy"');
    console.log('Committed files');
  } catch (e) {
    console.log('Nothing to commit');
  }

  console.log('Pushing to remote...');
  execSync(`git push -f ${repoUrl} gh-pages`);
  console.log('Deployment successful!');

} catch (error) {
  console.error('Deployment failed:', error.message);
  process.exit(1);
}
