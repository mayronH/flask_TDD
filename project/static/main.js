const postElements = document.querySelectorAll('.entry');

postElements.forEach((postElement) => {
	postElement.addEventListener("click", function(){
		const postId = postElement.children[0].getAttribute("id");
		const node = this;
		
		fetch(`/delete/${postId}`)
			.then(function (resp){
				return resp.json()
			})
			.then(function(result) {
				if (result.status === 1){
					node.parentNode.removeChild(node)
				}
				location.reload()
			})
			.catch(function (err){
				console.log(err)
			})
	})
})