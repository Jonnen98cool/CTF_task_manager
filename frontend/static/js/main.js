async function main()
{
	//Start asynchronously fetching backend database containing all of the non-static data to display
  	const startedFetch = fetchLanding();

	//"Add challenge" button event listener
	const addChallengeForm = document.getElementById("addChallengeDiv").querySelector("form");
	addChallengeForm.addEventListener("submit", (e) =>
	{
	  e.preventDefault();
	  const cnameInput = addChallengeForm.querySelector("input");
	  if (cnameInput.value == "") { alert("Please input a challenge name."); }
	  else { fetchAddChallenge(cnameInput.name, cnameInput.value); cnameInput.value = ""; }
	});


	//From this point onwards we need the API results
	const dbContents = await startedFetch;
	if(dbContents == null) { return "ERROR: dbContents was null"; }
  	
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

	//Create all challenge containers, then populate them appropriately
	const challengeContainer = document.getElementById("challenge_container");
	const dbOuter = dbContents["challengesOuter"];
	const dbInner = dbContents["challengesInner"];
	createChallengeDivBase(jsonData=dbOuter, parentContainer=challengeContainer);
	populateChallengeDiv(jsonData=dbInner);
	
	return "END OF MAIN REACHED";
}



(async () => 
{
	const mainReturn = await main();
	console.log(mainReturn);
}) ();
