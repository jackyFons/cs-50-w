document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});


// Shows view to compose an email.
function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display= 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

// When a user submits the email composition form, send the email
function send_email(ev) {

  ev.preventDefault()

  // POST to send email
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(() => load_mailbox('sent'));

}

// Loads emails
function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  const emails_view = document.querySelector('#emails-view');
  emails_view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Get emails
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    console.log(emails);

    // Loop through every email
    emails.forEach(email => {
      // Create <div> for email
      let email_div = document.createElement('div');
      email_div.innerHTML = `<div class='preview-sender'>${email['sender']}</div>
                             <div class='preview-subject'>${email['subject']}</div>
                             <div class='preview-timestamp'>${email['timestamp']}</div>`;

      email_div.className = email['read'] ? 'email-div read' : 'email-div unread';

      // Add listener to <div>
      email_div.addEventListener('click', () => load_email(mailbox, email['id']));

      // Add the <div> to the emails_view
      emails_view.append(email_div);
    });
  });
}

// Loads the email that was clicked
function load_email(view, id) {

  // Show email and hide other views
  document.querySelector('#email-view').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Get email based on id parameter
  fetch('/emails/' + id)
  .then(response => response.json())
  .then(email => {
    // Print email
    console.log(email);

    // Mark email as read if it was unread
    if (!email['read']) {
      change_read_status(email, id, false);
    }

    // Add email contents to view
    document.querySelector('#email-header').innerHTML = `
      <div>
        <b>From:</b> ${email['sender']}
        <span class='left-space preview-timestamp'>${email['timestamp']}</span>
      </div>
      <div>
        <b>To:</b> ${email['recipients']}
      </div>`;

    document.querySelector('#email-body').innerHTML = `
      <div class='body-padding'><b>${email['subject']}</b></div>
      <hr/>
      <div class='body-padding'>${email['body']}</div>`;

    // Change archive button's display and add an event listener
    archive_init(view, email['id'], email['archived']);

    // Add event listener to reply button
    document.querySelector('#reply').addEventListener('click', ()=>reply(email));

  });
}


// Function to change email's read status
function change_read_status(email, id, bool) {
  fetch('/emails/'+id, {
    method: 'PUT',
    body: JSON.stringify({
      read: bool
    })
  })
}


// Change archive button
function archive_init(view, id, bool) {
  let archive_button = document.querySelector('#archive');

  // Hide button if the email is a 'sent' email
  if (view == 'sent') {
        archive_button.style.display = 'none';
  }
  // Update button text and add event listener
  else {
    archive_button.innerText = bool ? 'Unarchive' : 'Archive';
    archive_button.addEventListener('click', ()=>archived_button_clicked(id, bool));
  }
}


// Changes archive status
function archived_button_clicked(id, bool) {
  fetch('/emails/' + id, {
    method: 'PUT',
    body: JSON.stringify ({
      archived: !bool
    })
  })
  .then(document.querySelector('#archive').innerText = bool ? 'Archive' : 'Unarchive');
}


function reply(email) {
  // Change view
  compose_email();

  // Pre-fill the view
  document.querySelector('#compose-recipients').value = email['sender'];
  document.querySelector('#compose-subject').value =
    email['subject'].startsWith('Re: ') ? email['subject'] : 'Re: ' + email['subject'];
  document.querySelector('#compose-body').value = `On ${email['timestamp']}, ${email['sender']} wrote:\n${email['body']}`;
}