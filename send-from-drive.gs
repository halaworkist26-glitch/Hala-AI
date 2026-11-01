// Sends the HTML files in a Google Drive folder through Gmail.
// 1. Upload the files from the "emails" folder to a Drive folder named as below.
// 2. Paste this into a new project at script.google.com.
// 3. Run sendTest. It sends the first file to MY_EMAIL only, so you can check it.
// 4. Run sendBatch. Sent files move to a "Sent" subfolder, so nothing goes out twice.

const FOLDER_NAME = 'Campaign Emails';
const MY_EMAIL = '44hala2003@gmail.com';
const SENDER_NAME = 'Hala Al-Attiyat';
const MAX_PER_RUN = 20;
const PAUSE_MS = 15000;

function sendTest() {
  const files = listEmails(getFolder());
  if (!files.length) throw new Error('No HTML files in "' + FOLDER_NAME + '"');
  const email = parseEmail(files[0]);
  deliver(MY_EMAIL, '[TEST for ' + email.to + '] ' + email.subject, email);
  Logger.log('Test of ' + files[0].getName() + ' sent to ' + MY_EMAIL);
}

function sendBatch() {
  const folder = getFolder();
  const sentFolder = getSubfolder(folder, 'Sent');
  const files = listEmails(folder).slice(0, MAX_PER_RUN);

  files.forEach(function (file, index) {
    const email = parseEmail(file);
    deliver(email.to, email.subject, email);
    file.moveTo(sentFolder);
    Logger.log('Sent ' + file.getName() + ' to ' + email.to);
    if (index < files.length - 1) Utilities.sleep(PAUSE_MS);
  });
  Logger.log('Sent ' + files.length + ' this run. Remaining: ' + listEmails(folder).length);
}

function deliver(to, subject, email) {
  GmailApp.sendEmail(to, subject, email.plain, {
    htmlBody: email.html,
    name: SENDER_NAME,
  });
}

function parseEmail(file) {
  const raw = file.getBlob().getDataAsString('UTF-8');
  const to = raw.match(/<meta name="x-send-to" content="([^"]+)">/);
  const subject = raw.match(/<title>([^<]*)<\/title>/);
  const plain = raw.match(/<!--PLAINTEXT\n([\s\S]*?)\nPLAINTEXT-->/);
  if (!to || !subject || !plain) throw new Error('Missing details in ' + file.getName());

  return {
    to: to[1],
    subject: decodeEntities(subject[1]),
    plain: plain[1],
    html: raw.replace(to[0] + '\n', '').replace(plain[0] + '\n', ''),
  };
}

function decodeEntities(text) {
  return text.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
}

function listEmails(folder) {
  const found = [];
  const files = folder.getFiles();
  while (files.hasNext()) {
    const file = files.next();
    if (/\.html$/i.test(file.getName())) found.push(file);
  }
  return found.sort(function (a, b) {
    return a.getName() < b.getName() ? -1 : 1;
  });
}

function getFolder() {
  const folders = DriveApp.getFoldersByName(FOLDER_NAME);
  if (!folders.hasNext()) throw new Error('Create a Drive folder named "' + FOLDER_NAME + '"');
  return folders.next();
}

function getSubfolder(folder, name) {
  const existing = folder.getFoldersByName(name);
  return existing.hasNext() ? existing.next() : folder.createFolder(name);
}
