document.addEventListener('DOMContentLoaded', function () {
  handleAddButtonLandingPage()
  getEmailWithType('inbox')
  getCurrentUser()

  // Web Socket
  triggerArchiveWebSocket()
  triggerComposeWebSocket()
  triggerReadWebSocket()
})

function triggerArchiveWebSocket() {
  const archive = `ws://127.0.0.1:8000/ws/emails/archive`
  const archiveSocket = new WebSocket(archive)

  archiveSocket.onopen = function (e) {
    console.log('WebSocket Connected', e)
  }

  archiveSocket.onerror = function (e) {
    console.log('WebSocket have error', e)
  }

  archiveSocket.onclose = function (e) {
    console.log('WebSocket Disconnected', e)
  }

  archiveSocket.onmessage = function (e) {
    const data = JSON.parse(e.data)
    const type = window.type
    const { archived, content } = data
    if (content.user != window.currentUser) return
    if (type === 'inbox' && !window.archiveSender) {
      if (archived) {
        const element = document.querySelector(`#id-${content.id}`)
        if (!!element) element.remove()
      } else {
        const emailViewer = document.querySelector('#emails-view')
        const currentTime = new Date(content.timestamp)
        const listTime = []
        const listElement = document.querySelectorAll('.timestamp')
        listElement.forEach((item) => listTime.push(new Date(item.innerHTML)))
        let positionElement
        for (let i = 0; i < listTime.length; i++) {
          if (listTime[i] < currentTime) {
            positionElement = listElement[i]
            break
          } else continue
        }
        addEmailToDOM(content, emailViewer, positionElement)
      }
    }
    if (type === 'archive' && !window.archiveSender) {
      if (!archived) {
        const element = document.querySelector(`#id-${content.id}`)
        if (!!element) element.remove()
      } else {
        const emailViewer = document.querySelector('#emails-view')
        const currentTime = new Date(content.timestamp)
        const listTime = []
        const listElement = document.querySelectorAll('.timestamp')
        listElement.forEach((item) => listTime.push(new Date(item.innerHTML)))
        let positionElement
        for (let i = 0; i < listTime.length; i++) {
          if (listTime[i] < currentTime) {
            positionElement = listElement[i]
            break
          } else continue
        }
        addEmailToDOM(content, emailViewer, positionElement)
      }
    }
    window.archiveSender = false
    console.log('WebSocket receive message', e)
  }
  window.archiveSocket = archiveSocket
}

function triggerReadWebSocket() {
  const read = `ws://127.0.0.1:8000/ws/emails/read`
  const readSocket = new WebSocket(read)

  readSocket.onopen = function (e) {
    console.log('WebSocket Connected', e)
  }

  readSocket.onerror = function (e) {
    console.log('WebSocket have error', e)
  }

  readSocket.onclose = function (e) {
    console.log('WebSocket Disconnected', e)
  }

  readSocket.onmessage = function (e) {
    const data = JSON.parse(e.data)
    const { id, user } = data.content
    if (user != window.currentUser) return
    if (!window.readSocketSender) {
      const element = document.querySelector(`#id-${id}`)
      if (!!element) {
        const className = element.className
        if (className === 'list_email_item') element.className = 'list_email_item_unread'
        else if (className === 'list_email_item_unread') element.className = 'list_email_item'
      }
    }
    window.readSocketSender = false
    console.log('WebSocket receive message', e)
  }
  window.readSocket = readSocket
}
async function sendEmailRequest(event) {
  event.preventDefault()
  const recipients = document.querySelector('#compose_email_recipients').value
  const senderUser = document.querySelector('#compose_sender').value
  let content = {
    subject: document.querySelector('#compose_email_subject').value,
    body: document.querySelector('#compose_email_body').value,
    recipients: recipients,
  }

  const response = await fetch('/emails', {
    method: 'POST',
    body: JSON.stringify(content),
  })
  content = await response.json()
  await window.composeSocket.send(
    JSON.stringify({
      senderUser: senderUser,
      content: content,
      recipients: recipients,
    })
  )
  window.composeSender = true
  getEmailWithType('sent')
}

function triggerComposeWebSocket() {
  const compose = `ws://127.0.0.1:8000/ws/emails/compose`
  const composeSocket = new WebSocket(compose)

  composeSocket.onopen = function (e) {
    console.log('WebSocket Connected', e)
  }

  composeSocket.onerror = function (e) {
    console.log('WebSocket have error', e)
  }

  composeSocket.onclose = function (e) {
    console.log('WebSocket Disconnected', e)
  }

  composeSocket.onmessage = function (e) {
    const data = JSON.parse(e.data)
    const type = window.type
    const { senderUser, content, recipients } = data
    if (
      !window.composeSender &&
      ((senderUser === window.currentUser && type === 'sent') ||
        (recipients.includes(window.currentUser) && type === 'inbox'))
    ) {
      if (senderUser === window.currentUser && type === 'sent') content.read = true
      const emailViewer = document.querySelector('#emails-view')
      addEmailToDOM(content, emailViewer, null, true)
    }
    window.composeSender = false
    console.log('WebSocket receive message', e)
  }
  window.composeSocket = composeSocket
}

function getCurrentUser() {
  const currentUser = document.querySelector('#current-user').innerHTML
  window.currentUser = currentUser
}

function addEmailToDOM(emailItem, emailViewerArgument, positionElement, isInsertTop = false) {
  let div = document.createElement('div')
  div.className = emailItem['read'] ? 'list_email_item' : 'list_email_item_unread'
  div.id = `id-${emailItem.id}`
  div.innerHTML = `
      <span class="sender col-3"> <b>${emailItem['sender']}</b> </span>
      <span class="subject col-6"> ${emailItem['subject']} </span>
      <span class="timestamp col-3"> ${emailItem['timestamp']} </span>
  `

  div.addEventListener('click', () => getContentForEmail(emailItem['id']))
  if (!positionElement) {
    if (!isInsertTop) emailViewerArgument.appendChild(div)
    else {
      const child = emailViewerArgument.firstChild.nextElementSibling
      emailViewerArgument.insertBefore(div, child)
    }
  } else {
    positionElement.parentElement.before(div)
  }
}
function handleAddButtonLandingPage() {
  document.querySelector('#inbox').addEventListener('click', () => getEmailWithType('inbox'))
  document.querySelector('#sent').addEventListener('click', () => getEmailWithType('sent'))
  document.querySelector('#archived').addEventListener('click', () => getEmailWithType('archive'))
  document.querySelector('#compose').addEventListener('click', getComposeView)
  document.querySelector('#compose-form').addEventListener('submit', sendEmailRequest)
}
function getComposeView() {
  handleDomElement('composeStyle')
  handleDomElement('composeValue')
}

async function getContentForEmail(id) {
  const response = await fetch('/emails/' + id)
  const emailFetched = await response.json()

  handleDomElement('getContentEmail')

  const emailViewer = addEmailInfoAndReturnDomElement()

  const listButton = [
    buildButtonLogic('reply', emailFetched),
    buildButtonLogic('archive', emailFetched),
    buildButtonLogic('makeReadLater', emailFetched),
  ]

  listButton.forEach((button) => {
    emailViewer.appendChild(button)
  })

  if (!emailFetched['read']) {
    await fetch('/emails/' + emailFetched['id'], {
      method: 'PUT',
      body: JSON.stringify({ read: true }),
    })
    const content = { id: emailFetched['id'], user: window.currentUser }
    await window.readSocket.send(
      JSON.stringify({
        content: content,
      })
    )
    window.readSocketSender = true
  }

  function addEmailInfoAndReturnDomElement() {
    const emailViewer = document.querySelector('#email-view')
    emailViewer.innerHTML = `
      <ul class="list-group">
        <li class="list-group-item"><b>From:</b> <span>${emailFetched['sender']}</span></li>
        <li class="list-group-item"><b>To: </b><span>${emailFetched['recipients']}</span></li>
        <li class="list-group-item"><b>Subject:</b> <span>${emailFetched['subject']}</span</li>
        <li class="list-group-item"><b>Time:</b> <span>${emailFetched['timestamp']}</span></li>
      </ul>
      <p class="m-2">${emailFetched['body']}</p>
    `
    return emailViewer
  }

  function buildButtonLogic(typeOfButton, email) {
    if (typeOfButton === 'reply') {
      const replyEmailButtonLogic = document.createElement('button')
      replyEmailButtonLogic.className = 'btn-primary m-1'
      replyEmailButtonLogic.innerHTML = 'Reply'
      replyEmailButtonLogic.addEventListener('click', function () {
        getComposeView()

        document.querySelector('#compose_email_recipients').value = email['sender']
        let subject = email['subject']
        if (subject.split(' ', 1)[0] != 'Re:') {
          subject = 'Re: ' + subject
        }
        document.querySelector('#compose_email_subject').value = subject

        let body = `
        On ${email['timestamp']}, ${email['sender']} wrote: ${email['body']}
      `
        document.querySelector('#compose_email_body').value = body
      })
      return replyEmailButtonLogic
    }

    if (typeOfButton === 'archive') {
      const buttonArchiveLogic = document.createElement('button')
      buttonArchiveLogic.className = 'btn-primary m-1'
      buttonArchiveLogic.innerHTML = !email['archived'] ? 'Archive' : 'Unarchive'
      buttonArchiveLogic.addEventListener('click', async function () {
        const response = await fetch('/emails/' + email['id'], {
          method: 'PUT',
          body: JSON.stringify({ archived: !email['archived'] }),
        })
        const content = await response.json()
        content['user'] = window.currentUser
        await window.archiveSocket.send(
          JSON.stringify({
            archived: !email['archived'],
            content: content,
          })
        )
        window.archiveSender = true
        getEmailWithType('inbox')
      })
      return buttonArchiveLogic
    }
    if (typeOfButton === 'makeReadLater') {
      const makeReadLaterButton = document.createElement('button')
      makeReadLaterButton.className = 'btn-secondary m-1'
      makeReadLaterButton.innerHTML = 'Mark as Unread'
      makeReadLaterButton.addEventListener('click', async function () {
        await fetch('/emails/' + email['id'], {
          method: 'PUT',
          body: JSON.stringify({ read: false }),
        })
        const content = { id: email['id'], user: window.currentUser }
        await window.readSocket.send(
          JSON.stringify({
            content: content,
          })
        )
        window.readSocketSender = true
        getEmailWithType('inbox')
      })
      return makeReadLaterButton
    }
  }
}

function getEmailWithType(type) {
  window.type = type
  handleDomElement('inbox')
  getUserEmail(type)
}

function getMailBoxTitle(item) {
  const title = item.charAt(0).toUpperCase() + item.slice(1)
  return title
}

async function getUserEmail(type) {
  const emailViewer = document.querySelector('#emails-view')
  emailViewer.innerHTML = `<h2>${getMailBoxTitle(type)}</h2>`
  const fetchRequest = await fetch('/emails/' + type)
  const response = await fetchRequest.json()
  response.forEach((emailItem) => {
    addEmailToDOM(emailItem, emailViewer)
  })
}

function handleDomElement(type) {
  if (type === 'inbox') {
    document.querySelector('#email-view').style.display = 'none'
    document.querySelector('#compose-view').style.display = 'none'
    document.querySelector('#emails-view').style.display = 'block'
  }

  if (type === 'composeStyle') {
    document.querySelector('#emails-view').style.display = 'none'
    document.querySelector('#email-view').style.display = 'none'
    document.querySelector('#compose-view').style.display = 'block'
  }

  if (type === 'composeValue') {
    document.querySelector('#compose_email_recipients').value = ''
    document.querySelector('#compose_email_subject').value = ''
    document.querySelector('#compose_email_body').value = ''
  }

  if (type === 'getContentEmail') {
    document.querySelector('#emails-view').style.display = 'none'
    document.querySelector('#compose-view').style.display = 'none'
    document.querySelector('#email-view').style.display = 'block'
  }
}
