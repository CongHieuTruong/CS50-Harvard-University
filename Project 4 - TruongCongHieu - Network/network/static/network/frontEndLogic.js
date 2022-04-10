var lastPost = null
document.addEventListener('DOMContentLoaded', function (event) {
  const headers = {
    Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-CSRFToken': 'ZzXaS82q71wtasBuRhuJFVGT7amTGp5NG5ySD9DEN13VV7SXezZKm4QCifa09Gyf',
  }
  triggerWebSocket()
  buildLogicLikeButton()
  buildEditLogicForm()
  addNewPostLogic()
  loadUserData()

  function triggerWebSocket() {
    const socialNetwork = `ws://127.0.0.1:8000/ws/user/social-network`
    const socialNetworkSocket = new WebSocket(socialNetwork)

    socialNetworkSocket.onopen = function (e) {
      console.log('WebSocket Connected', e)
    }

    socialNetworkSocket.onerror = function (e) {
      console.log('WebSocket have error', e)
    }

    socialNetworkSocket.onclose = function (e) {
      console.log('WebSocket Disconnected', e)
    }
    socialNetworkSocket.onmessage = function (e) {
      const { data } = JSON.parse(e.data)
      if (data.type === 'post') buildPost(data)

      if (data.type === 'like') {
        const likeButton = document.querySelector(`[datalikeid='${data.idPost}']`)
        likeButton.children[0].innerHTML = data.total_likes
        if (data.username === window.username && data.user_id === window.user_id)
          likeButton.className = data.css_class
      }

      if (data.type === 'edit') {
        const postContent = document.querySelector(`#post_text_${data.id}`)
        postContent.innerHTML = data.content
      }
      console.log('WebSocket receive message', e)
    }
    window.socialNetworkSocket = socialNetworkSocket
  }
  async function loadUserData() {
    const response = await fetch('/user', {
      method: 'GET',
      headers: headers,
    })
    const data = await response.json()
    window.email = data.email
    window.username = data.username
    window.user_id = data.user_id
  }

  function addNewPostLogic() {
    document.querySelector('#buttonSubmitPost')?.addEventListener('click', async () => {
      const content = document.querySelector('#content_new_post')?.value
      if (!content) return
      const response = await fetch('/post-message', {
        method: 'POST',
        body: JSON.stringify(content),
        headers: headers,
      })
      const data = await response.json()
      document.querySelector('#content_new_post').value = ''
      data['email'] = window.email
      data['username'] = window.username
      data['user_id'] = window.user_id
      data['type'] = 'post'
      await window.socialNetworkSocket.send(
        JSON.stringify({
          data: data,
        })
      )
    })
  }

  function buildPost(item) {
    const div = document.createElement('div')
    div.className = 'card'
    div.innerHTML = `<div class="rounderCard">
            <h5 class="cardUserNameAndLink"><a href="profile/${item.username}">${
      item.username
    }</a></h5>
            ${
              item.user_id === window.user_id
                ? `<a href='#' class='cardEditText' id='editButton_${item.id}' data-id='${item.id}' data-toggle='modal'>
                  Edit
                </a>`
                : ''
            }
            
            <p class="cardContentPost" id="post_text_${item.id}"> ${item.text}</p>
            ${
              item.user_id === window.user_id
                ? `<div id="edit_button_id${item.id}" data-id="${item.id}" style="display: none">
            <div class="textArea">
            <textarea
            class="form-control"
            id="editTextPostId${item.id}"
            placeholder="How are you today?"
          ></textarea>
            </div>
            <button type="button" data-id="${item.id}" id="buttonCloseEdit_${item.id}" class="btn btn-light"
                data-dismiss="modal">Close</button>
            <button class="btn btn-primary" id="buttonSaveEdit_${item.id}" queryId="${item.id}">Save changes</button>
        </div>`
                : ''
            }

            <p class="cardContentPost"><small class="small_text">${item.date}</small></p>
            <p class="cardContentPost">
                <div data-id="${item.id}" dataLikeId="${item.id}"
                    class="cardEditText far fa-heart">&nbsp<small
                        class="small_text">0</small></div>
            </p>
        </div>`
    document.querySelector('#posts').prepend(div)
    const editButton = document.querySelector(`#editButton_${item.id}`)
    buildEditButtonLogic(editButton)
    const buttonClose = document.querySelector(`#buttonCloseEdit_${item.id}`)
    buildCloseButtonEdit(buttonClose)
    const buttonSave = document.querySelector(`#buttonSaveEdit_${item.id}`)
    buildSaveButtonEdit(buttonSave, item.id)
    const likeButton = document.querySelector(`[dataLikeId='${item.id}']`)
    buildButtonLikeAndAPILogic(likeButton)
  }

  function buildSaveButtonEdit(button, id) {
    if (!button) return
    button.onclick = async function () {
      const contentElement = document.querySelector(`#editTextPostId${id}`)
      const content = contentElement?.value
      if (!content) return
      await fetch(`/editpost/${id}`, {
        method: 'POST',
        body: JSON.stringify(content),
        headers: headers,
      })
      const data = {}
      data['id'] = id
      data['content'] = content
      data['email'] = window.email
      data['username'] = window.username
      data['user_id'] = window.user_id
      data['type'] = 'edit'
      await window.socialNetworkSocket.send(
        JSON.stringify({
          data: data,
        })
      )
      const buttonClose = document.querySelector(`#buttonCloseEdit_${id}`)
      buttonClose.click()
    }
  }

  function buildButtonLikeAndAPILogic(button) {
    button.onclick = function () {
      sendLikeOrDislike(this)
    }
  }

  function buildLogicLikeButton() {
    const likeButtons = document.querySelectorAll('.fa-heart')
    likeButtons?.forEach((element) => buildButtonLikeAndAPILogic(element))
  }

  function buildEditLogicForm() {
    const buttonSaves = document.querySelectorAll("[id^='buttonSaveEdit_']")
    buttonSaves.forEach((button) => {
      const id = button.attributes.queryId.value
      buildSaveButtonEdit(button, id)
    })

    const editButtons = document.querySelectorAll("[id^='editButton_']")

    editButtons.forEach((button) => {
      buildEditButtonLogic(button)
    })

    const buttonCloses = document.querySelectorAll("[id^='buttonCloseEdit_']")

    buttonCloses.forEach((button) => {
      buildCloseButtonEdit(button)
    })
  }

  function buildCloseButtonEdit(button) {
    if (!button) return
    button.onclick = function () {
      hideEditForm(this)
    }
  }

  function buildEditButtonLogic(button) {
    if (!button) return
    button.onclick = function () {
      if (lastPost != null) {
        hideEditForm(lastPost)
      }
      lastPost = this
      const textMessage = document.querySelector('#post_text_' + this.dataset.id)
      const formSelector = document.querySelector('#edit_button_id' + this.dataset.id)
      textMessage.style.display = 'none'
      formSelector.querySelector('#editTextPostId' + this.dataset.id).value = textMessage.innerHTML
      formSelector.style.display = ''
    }
  }

  if (document.getElementById('followButton')) {
    document.querySelector('#followButton').addEventListener('click', async function (event) {
      const response = await fetch(`/follow/${this.dataset.id}`)
      const data = await response.json()
      document.querySelector('#sp_followers').innerHTML = data.total_followers
      if (data.result == 'follow') {
        this.innerHTML = 'Following'
        this.className = 'btn btn-primary'
      } else {
        this.innerHTML = 'Follow'
        this.className = 'btn btn-outline-primary'
      }
    })
    addEventHoverOnButtonFollow()
  }

  function addEventHoverOnButtonFollow() {
    document.querySelector('#followButton').addEventListener('mouseover', function () {
      if (this.className == 'btn btn-primary') {
        this.innerHTML = 'Un follow'
      }
    })

    document.querySelector('#followButton').addEventListener('mouseleave', function () {
      if (this.className == 'btn btn-primary') {
        this.innerHTML = 'Following'
      }
    })
  }

  async function sendLikeOrDislike(element) {
    const response = await fetch(`/like/${element.dataset.id}`)
    const data = await response.json()
    data['email'] = window.email
    data['username'] = window.username
    data['user_id'] = window.user_id
    data['type'] = 'like'
    window.socialNetworkSocket.send(
      JSON.stringify({
        data: data,
      })
    )
  }

  function hideEditForm(element) {
    const postText = document.querySelector('#post_text_' + element.dataset.id)
    const formSelector = document.querySelector('#edit_button_id' + element.dataset.id)
    postText.style.display = ''
    formSelector.querySelector('#editTextPostId' + element.dataset.id).value = postText.innerHTML
    formSelector.style.display = 'none'
  }
})
