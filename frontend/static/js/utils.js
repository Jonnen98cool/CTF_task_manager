//Globals
const markClasses = {
	"0": "markRed",			//I am attempting
	"1": "markOrange",		//I want to attempt later
	"2": "markYellow",		//I have made progress but stopped attempting
	"3": "markBlack",		//Here be dragons
	"4": "markRecommend",	//I think person X would be perfect for this
	"5": "markSolved",		//Solved (alternative to just deleting the entire challenge container)
	"6": "markRemove" 		//I don't wish to have a marking on this challenge								
};

let userList = [];	//Is going to get filled with usernames from the backend



//Creates challenges according to "jsonData" inside the container "container". 
function createChallengeDivBase(jsonData, parentContainer)
{
	//Loop through challenges, add a div for each challenge
	for (let i=0; i < jsonData.length; i++)
	{
		//Accquire values from json fields
	  	const id = jsonData[i]["id"];
	  	const name = jsonData[i]["name"];

  		//Create the div
		const challengeContainer = document.createElement("div");
		challengeContainer.classList.add("ChallengeBox");
		challengeContainer.id = "c_" + id;
	
		//Create header div, set title
		const containerHeader = document.createElement("div");
		containerHeader.classList.add("challengeBoxHeader");
		const challName = document.createElement("h3");
		challName.innerHTML = name;
		containerHeader.appendChild(challName);

		//Add delete challenge option to header
		const delBtn = document.createElement("button");
		delBtn.classList.add("deleteChallengeButton")
		delBtn.type = "button";
		delBtn.innerHTML = "Delete";
		delBtn.addEventListener("click", function() { fetchDeleteChallenge(id) } ); //Event handler for delete
		containerHeader.appendChild(delBtn);
		challengeContainer.appendChild(containerHeader);	//add header to main container
		
		//Add "Mark as..." button
		const markBtn = document.createElement("button");	
		markBtn.classList.add("markAsButton")
		markBtn.type = "button";
		markBtn.innerHTML = "Mark as...";

		//Add collapsible form which triggers on clicking "Mark as..." button
		const collapsibleMarkings = getMarkingCollapsible(id);
		markBtn.addEventListener("click", function() { toggleCollapse(collapsibleMarkings) } );
		challengeContainer.appendChild(markBtn);
		challengeContainer.appendChild(collapsibleMarkings);

		//Add div showing current user markings
		const markingsDiv = document.createElement("div");
		markingsDiv.classList.add("userMarkings");
		challengeContainer.appendChild(markingsDiv);
		
	  	parentContainer.appendChild(challengeContainer);
	}
}


//Returns what should appear when clicking "Mark as..." button
function getMarkingCollapsible(challId)
{
	//Create the collapsible div
	const collapsible = document.createElement("div");
	collapsible.classList.add("markCollapsible");

	//Create form, add text to it
	const markForm = document.createElement("form");
	const formText = document.createElement("p");
	formText.innerHTML = "Select a marking:";
	markForm.appendChild(formText);

	//Add radio button options to form
	for (let i=0; i < Object.keys(markClasses).length; i++)	 //You cant do dictionary.length, you have to do like this
	{
		//Each radio button input is inside a label. This allows for some CSS magic
		const radioLabel = document.createElement("label");
		radioLabel.classList.add("markLabel"); 
		radioLabel.classList.add(markClasses[i.toString()]); //Dual classes	

		//Creating the radio buttons, adding the inside the label
		const radioBtn = document.createElement("input");
		radioBtn.classList.add(markClasses[i.toString()]);
		radioBtn.type = "radio";
		radioBtn.name = "marking";
		radioBtn.value = i;				//Value is int, not str
		radioLabel.appendChild(radioBtn);

		//Set empty span inside label, needed for CSS to make border appear on radio button select (difficult/unsupported to modify the parent label in css)
		const radioSpan = document.createElement("span");
		radioLabel.appendChild(radioSpan);
		
		markForm.appendChild(radioLabel);
	}

	//"Mark" submit button
	const submitBtn = document.createElement("input");
	submitBtn.classList.add("markButton");
	submitBtn.type = "submit";
	submitBtn.value = "Mark";
	markForm.appendChild(submitBtn);
	
	//Event listeneder on the marking form. If blue radio button is clicked:  display: block on the user list menu
	const markRecommendRadio = markForm.querySelector(".markRecommend").querySelector("input");
	markForm.addEventListener("change", function() 
	{
		 if(markRecommendRadio.checked) { collapsibleUserList.style.display = "block"; }
		 else							{ collapsibleUserList.style.display = "none"; }
	} );

	//Add event listener on the "Mark" submit button, which takes into consideration both selected marking and potential recommended user as inputs.
	const collapsibleUserList = getCollapsibleUserList(challId);
	const userListForm = collapsibleUserList.querySelector("form");
	submitBtn.addEventListener("click", function(e) { e.preventDefault(); fetchMarkChallenge(challId, getSelectedRadioValue(markForm), getSelectedRadioValue(userListForm)) } );


	//Add the created elements to the collapsible div
	collapsible.appendChild(markForm);				//Marking form
	collapsible.appendChild(collapsibleUserList);	//User list form
	collapsible.style.display = "none";		//Not shown by default
	
	return collapsible;
}


//Returns the form from which a recommended user can be selected. This appears when the ".markRecommend" radio button is selected.
function getCollapsibleUserList(challId)
{
	//Users must be fetched from api before this function is called. This entails populating the global "userList"
	if(userList.length == 0) { console.log("ERROR: getCollapsibleUserList(): userList was empty"); return; }
	
	const collapsibleUsers = document.createElement("div");
	collapsibleUsers.classList.add("userListCollapsible");

	//Create form
	const selectUserForm = document.createElement("form");
	formText = document.createElement("p");
	formText.innerHTML = "Select a user:";
	selectUserForm.appendChild(formText);

	//Add radio button options to form
	for (let i=0; i < userList.length; i++)
	{
		//Label which will contain radio button. I do it this way as to allow for selecting the tiny radio button by clicking on the associated username.
		const radioLabel = document.createElement("label");

		//Add radio button to label
		const radioBtn = document.createElement("input");
		radioBtn.type = "radio";
		radioBtn.name = "user";
		radioBtn.value = userList[i];
		radioLabel.appendChild(radioBtn);

		//Add username to label
		const usernameSpan = document.createElement("span");
		usernameSpan.innerHTML = userList[i];
		radioLabel.appendChild(usernameSpan);

		//Add created label object to form
		selectUserForm.appendChild(radioLabel);
		selectUserForm.appendChild(document.createElement("br"));
	}

	collapsibleUsers.appendChild(selectUserForm);
	collapsibleUsers.style.display = "none";		//Not shown by default
	return collapsibleUsers;
}



//Given a form, get corresponding radio buttons and check which one was selected prior to submitting the form (this function gets called on form submit). Return that radio button's value, or -1 if no radio button was selected.
function getSelectedRadioValue(form)	
{
	let retVal = -1;
	const radios = form.querySelectorAll("input");
	for (let i=0; i < radios.length; i++)
	{
    	if(radios[i].checked)
    	{
    		retVal = radios[i].value;
    		break;
    	}
   	}

	return retVal;
}


//Given an object, set its display property to either "none" or "block"
function toggleCollapse(object)
{
    if (object.style.display !== "none") { object.style.display = "none"; } 
    else 								 { object.style.display = "block"; }
}


//Given json data, populate each challenge container's .userMarkings div. 
function populateChallengeDiv(jsonData)
{
	//Loop through challengesInner, populate each challenge
	for (let i=0; i < jsonData.length; i++)
	{
	  	const id = jsonData[i]["challengeId"];
	  	const user = jsonData[i]["user"];
	  	const mark = jsonData[i]["mark"];
	  	const rec_usr = jsonData[i]["recommended_user"];

	 	const challengeContainer = document.getElementById("c_" + id);
		const markingsContainer = challengeContainer.querySelector(".userMarkings");
		const markingsEntry = document.createElement("div");
		markingsEntry.classList.add("markingsEntry");

		//Add the colored square (just a <p> with css)
	 	const userMarking = document.createElement("p");
	 	userMarking.classList.add("coloredP");
		userMarking.classList.add(markClasses[mark.toString()]);
		markingsEntry.appendChild(userMarking);

		//Add the username who marked it
		const markingUser = document.createElement("p");
		markingUser.classList.add("markingUsernameText");
		markingUser.innerHTML = " : " + user;
		markingsEntry.appendChild(markingUser);
		
		//Handling the special "recommend other user" marking
		if(rec_usr != null)
		{
			// "... recommends:"
			const recommendP = document.createElement("span");
			recommendP.classList.add("markingRecommendText");
			recommendP.innerHTML = "... recommends:";
			markingsEntry.appendChild(recommendP);

			//Recommended user
			const recommendedUser = document.createElement("span");
			recommendedUser.classList.add("markingRecommendUserText");
			recommendedUser.innerHTML = rec_usr;
			markingsEntry.appendChild(recommendedUser);

			//If someone recommended YOU to do the challenge, highlight it
			if(rec_usr == getCookieValue("user")) { recommendedUser.classList.add("challengeForYou"); }
		}

		markingsContainer.appendChild(markingsEntry);


		//If any user marked it as complete, lower entire div opacity
		if(mark == "5") { challengeContainer.style.opacity = 0.25; }

	 	//Challenges which have any marking should have background color set to X
		challengeContainer.style.backgroundColor = "DarkSlateGray";
	}
}


//Absolutley astonishing that this isn't built in to javascript
//Copied from https://www.w3schools.com/js/js_cookies.asp
function getCookieValue(name)
{
	let target = name + '=';
	let allCookies = decodeURIComponent(document.cookie);
	let cky = allCookies.split(';');

	for(let i=0; i < cky.length; i++)
	{
		let currentCookie = cky[i];
		while (currentCookie.charAt(0) == ' ') { currentCookie = currentCookie.substring(1); }
		if (currentCookie.indexOf(target) == 0) { return currentCookie.substring(target.length, currentCookie.length); }
	}
  
  return "NONEXISTENT-COOKIE";
}


function redirectUnauthorized()
{
	//Browser refuses to render backend-served 302 redirect content. Will have to do clientside redirects. EDIT: I think this was only when I tried to 302 redirect to the same site I was currently on. Oh well, this is working so I am keeping it.
	window.location.href = serverURL + "/static/html/unauth.html";		
}
