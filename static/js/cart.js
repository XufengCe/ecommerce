

var updateBtns = document.getElementsByClassName('update-cart')


for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        if (this.dataset.description == undefined) {
            var description = ""
        }
        description = this.dataset.description
        
        console.log('productId:', productId, 'action:', action, 'description:', description)

        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            addCookieItem(productId, action, description)
        }else{
            updateUserOrder(productId, action, description)
        }
    })
}

    

function addCookieItem(productId, action, description){
    console.log('User is not authenticated')
    console.log(productId, action, description)
    productId = productId + "-" + description
    if (action == 'add'){
        if (cart[productId] == undefined){
            cart[productId] = {'quantity':1}
        }else{
            cart[productId]['quantity'] += 1
        }
        if(description != undefined){
            
            cart[productId]['description'] = description
            
            console.log(description)
        }
    }
    if (action == 'remove'){
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0){
            console.log('Remove Item')
            delete cart[productId]
        }
    }



    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()

}

function updateUserOrder(productId, action, description){
    console.log('User is authenticated, sending data...')
    var url = '/update_item/'
    
    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId': productId, 'action': action, 'description': description})
    })

    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        location.reload()
    })
}



