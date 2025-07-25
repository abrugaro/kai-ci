import { appendFileSync } from 'fs';

const repoOwner = 'konveyor';
const repoName = 'editor-extensions';
const releaseTag = 'development-builds';
const token = process.env.GITHUB_TOKEN;

/**
 * Gets the latest dev build from https://github.com/konveyor/editor-extensions/releases/tag/development-builds
 * and appends the link and vsix file name to the .env file
 * @return {Promise<void>}
 */
async function main() {
  const res = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/releases/tags/${releaseTag}`);
  const data = await res.json();
  console.log(data);

  const asset = data.assets.findLast((a) => a.name.endsWith('.vsix'));
  if (!asset) {
    throw new Error('No .vsix asset found in release');
  }

  const envContent = `\nVSIX_FILE_NAME=${asset.name}\nDEFAULT_VSIX_DOWNLOAD_URL=${asset.browser_download_url}\n`;
  appendFileSync('.env', envContent);
  console.log('Generated .env with latest VSIX info');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
