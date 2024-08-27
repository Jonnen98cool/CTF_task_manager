async function main()
{
	//Start asynchronously fetching backend database containing all of the non-static data to display
  	const startedFetch = fetchLanding();

	//"Add Challenge Category" button event listener
	const addCategoryForm = document.getElementById("addCategoryDiv").querySelector("form");
	addCategoryForm.addEventListener("submit", (e) =>
	{
	  e.preventDefault();
	  const cCategoryInput = addCategoryForm.querySelector("input");
	  if (cCategoryInput.value == "") { alert("Please input a category name."); }
	  else { fetchAddCategory(cCategoryInput.name, cCategoryInput.value); cCategoryInput.value = ""; }
	});

	//"Add challenge" button event listener
	const addChallengeForm = document.getElementById("addChallengeDiv").querySelector("form");
	addChallengeForm.addEventListener("submit", (e) =>
	{
	  e.preventDefault();
	  const cnameInput = addChallengeForm.querySelector("input");
	  const ccategorySelect = addChallengeForm.querySelector("select");
	  if (cnameInput.value == "") { alert("Please input a challenge name."); }
	  else if (ccategorySelect.value == "none") { alert("Please select a category for this challenge."); }
	  else { fetchAddChallenge(cnameInput.value, ccategorySelect.value); cnameInput.value = ""; }
	});



	//From this point onwards we need the API data
	const dbContents = await startedFetch;
	if(dbContents == null) { return "ERROR: something went wrong with the fetch, dbContents was null"; }
  	
	// Set title
  	const titleApiValue = dbContents["siteInfo"][0]["ctf_title"];
  	const title = document.getElementById("ctfTitle");
  	title.innerHTML = titleApiValue;

	//Populate global var userList with a list of registered usernames
	const users = dbContents["users"];
	for (let i=0; i < Object.keys(users).length; i++)
	{
		userList.push(users[i]["username"]);
	}

	//Add challenge categories
	const challengeContainer = document.getElementById("challenge_container");
	const categories = dbContents["challengeCategories"];
	populateCategoryOptions(jsonData=categories);
	createChallengeCategory(jsonData=categories, parentContainer=challengeContainer);

	//Add challenge divs
	const dbOuter = dbContents["challengesOuter"];
	createChallengeDivBase(jsonData=dbOuter);

	//Populate challenge divs
	const dbInner = dbContents["challengesInner"];
	populateChallengeDiv(jsonData=dbInner);
	
	return "END OF MAIN REACHED";
}



(async () => 
{
	const mainReturn = await main();
	console.log(mainReturn);
}) ();
