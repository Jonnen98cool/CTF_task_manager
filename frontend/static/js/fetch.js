//This can be eg:
//	- http://localhost:5001
//	- http://1.2.3.4:9999
const serverURL = window.location.origin;


// This fetches the json from the backend server
async function fetchLanding()
{
 	const url = serverURL + "/api";
	const res = await fetch(url);
	let retVal = null;
	
	if(res.status == 401) { redirectUnauthorized(); return null; }
	else if(!res.ok)
	{
		const message = await res.text();
		alert(`Server message: ${message}`);
		//location.reload();		//Wouldn't this cause an infinite loop if something continuously went wrong
	}
	else
	{
		const json = await res.json();
		retVal = json;
	}

	return retVal;
}


async function fetchAddChallenge(param, value)
{
	const url = serverURL + "/api/add_challenge";
	const encodedData = encodeURIComponent(value);
	const req = {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		body: param + "=" + encodedData
	};

	const res = await fetch(url, req);
	if(res.status == 401) { redirectUnauthorized(); return; }
	else if(!res.ok)				//A 302 response is apparently considered res.ok, thought it was just 2xx
	{
		const message = await res.text();
		alert(`Server message: ${message}`);
	}
	
	location.reload();	//Independent on if res was ok, reload /
}


async function fetchDeleteChallenge(id)
{
	const url = serverURL + "/api/delete_challenge/" + id;	
	const req = { method: "DELETE" }

	const res = await fetch(url, req);
	if(res.status == 401) { redirectUnauthorized(); return; }
	else if(!res.ok)
	{
		const message = await res.text();
		alert(`Server message: ${message}`);
	}

	location.reload(); //Independent on if res was ok, reload /
}


async function fetchMarkChallenge(challId, mark, recommendedUser)
{
	if(mark == -1) { alert("Please select a mark alternative first."); return; } 
	else if(mark == 4 && recommendedUser == -1) { alert("Please select a user for the recommendation."); return; }
	
	const url = serverURL + "/api/update_challenge";
	let jsonifiedData = null
	if(mark == 4) 	{ jsonifiedData = `{"challengeId": ${challId}, "mark": ${mark}, "recommendedUser": "${recommendedUser}"}`; }
	else			{ jsonifiedData = `{"challengeId": ${challId}, "mark": ${mark}}`; }
	const req = {
	method: "POST",
	headers: {
		"Content-Type": "application/json"
	},
	body: jsonifiedData
	};

	const res = await fetch(url, req);
	if(res.status == 401) { redirectUnauthorized(); return;}
	else if(!res.ok)
	{
		const message = await res.text();
		alert(`Server message: ${message}`);
	}

	location.reload();	//Independent on if res was ok, reload /
}
