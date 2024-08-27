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
		alert(`Server message: \n\n${message}`);
		//location.reload();		//Wouldn't this cause an infinite loop if something continuously went wrong
	}
	else
	{
		const json = await res.json();
		retVal = json;
	}

	return retVal;
}


async function fetchAddCategory(param, value)
{
	const url = serverURL + "/api/add_category";
	const encodedCategoryName = encodeURIComponent(value);
	const req = {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		body: param + "=" + encodedCategoryName
	};

	standardResponse(url, req)
}

async function fetchDeleteCategory(id)
{
	const url = serverURL + "/api/delete_category/" + id;
	const req = { method: "DELETE" }

	standardResponse(url, req)
}


async function fetchAddChallenge(cName, cCategory)
{
	const url = serverURL + "/api/add_challenge";
	const encodedName = JSON.stringify(new String(cName));
	const encodedCategory = JSON.stringify(new String(cCategory));
	const jsonData = `{"cname": ${encodedName}, "ccategory": ${encodedCategory}}`;
	const req = {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: jsonData
	};

	standardResponse(url, req)
}


async function fetchDeleteChallenge(id)
{
	const url = serverURL + "/api/delete_challenge/" + id;	
	const req = { method: "DELETE" }

	standardResponse(url, req)
}


async function fetchMarkChallenge(challId, mark, recommendedUser)
{
	if(mark == -1) { alert("Please select a mark alternative first."); return; } 
	else if(mark == 4 && recommendedUser == -1) { alert("Please select a user for the recommendation."); return; }
	
	const url = serverURL + "/api/mark_challenge";
	let jsonifiedData = null
	const encodedUsername = JSON.stringify(new String(recommendedUser));
	if(mark == 4) 	{ jsonifiedData = `{"challengeId": ${challId}, "mark": ${mark}, "recommendedUser": ${encodedUsername}}`; }
	else			{ jsonifiedData = `{"challengeId": ${challId}, "mark": ${mark}}`; }
	const req = {
	method: "POST",
	headers: {
		"Content-Type": "application/json"
	},
	body: jsonifiedData
	};

	standardResponse(url, req)
}


async function fetchCommentChallenge(challId, comment)
{
	const url = serverURL + "/api/comment_challenge";
	const encodedComment = JSON.stringify(new String(comment));
	const jsonData = `{"challengeId": ${challId}, "comment": ${encodedComment}}`;
	const req = {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: jsonData
	};

	standardResponse(url, req)
}


async function standardResponse(url, req)
{
	const res = await fetch(url, req);
	if(res.status == 401) { redirectUnauthorized(); return; }
	else if(!res.ok)				//A 302 response is apparently considered res.ok, thought it was just 2xx
	{
		const message = await res.text();
		alert(`Server message: \n\n${message}`);
	}
	
	location.reload();	//Independent on if res was ok, reload /
}
