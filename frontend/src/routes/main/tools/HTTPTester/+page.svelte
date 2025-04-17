<script lang="ts">
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';

	let httpInput = [
    { id: "url", label: "Target URL", type: "text", value: "", example: "Ex: https://example.com", required: true },
		{ id: "method", label: "HTTP Method", type: "select", options: ["GET", "POST", "PUT"], value: "GET", required: true },
    { id: "header", label: "Header", type: "number", value: "", example: "Ex: application/json", required: true },
    { id: "cookies", label: "Cookies", type: "text", value: "", example: "Ex: csrf_token", required: true },
    { id: "hideStatus", label: "Hide Status Code", type: "text", value: "", example: "Ex: 403, etc.", required: true },
    { id: "showStatus", label: "Show Only Status Code", type: "text", value: "", example: "Ex: 200, 500, etc", required: true },
    { id: "proxy", label: "Proxy", type: "text", value: "", example: "Ex: https://proxy.example.com:3128", required: true },
    { id: "request", label: "Request Body", type: "text", value: "", example: "NULL", required: true },
    { id: "addParams", label: "Additional Parameters", type: "text", value: "", example: "NULL", required: false }
  ];

  let httpParams = {
    url: "",
    method: "",
    header: "",
    cookies: "",
    hideStatus: "",
    showStatus: "",
    proxy: "",
    request: "",
    addParams: ""
  };

	let errorMessages = {
    url: "",
    method: "",
    header: "",
    cookies: "",
    hideStatus: "",
    showStatus: "",
    proxy: "",
    request: ""
  };
  
	let jsonInput = `{
		"url": "http://example.com",
		"depth": "",
		"max_pages": "2",
		"user_agent": "",
		"delay": "",
		"proxy": ""
		}`;
	let response = writable(null);
	let loading = writable(false);
	let error = writable(null);
	let acceptingParams = true;
  
	async function sendToCrawler() {
	  loading.set(true);
	  error.set(null);
	  try {
		const res = await fetch('http://localhost:8000/crawl', {
		  method: 'POST',
		  headers: { 'Content-Type': 'application/json' },
		  body: jsonInput
		});
		const data = await res.json();
		response.set(data);
	  } catch (err) {
		error.set(err.message);
	  } finally {
		loading.set(false);
	  }
	}

	function validateParams() {
    let isValid = true;

		Object.keys(errorMessages).forEach(key => {
				errorMessages[key] = "";
			});

			if (!httpParams.url) {
				errorMessages.url = "URL is required!";
				isValid = false;
			}

			if (httpParams.method && !(httpParams.method == "get" || httpParams.method == "put" || httpParams.method == "post")) {
				errorMessages.method = "Valid Method is needed!";
				isValid = false;
			}

			if (!httpParams.header) {
				errorMessages.header = "Header is required!!";
				isValid = false;
			}

			if (!httpParams.cookies) {
				errorMessages.cookies = "Cookies are required!";
				isValid = false;
			}

			if (!httpParams.hideStatus) {
				errorMessages.hideStatus = "Hide Status Code is required!";
				isValid = false;
			}

			if (!httpParams.showStatus) {
				errorMessages.showStatus = "Show only Status Code is required!";
				isValid = false;
			}

			if (!httpParams.proxy) {
				errorMessages.proxy = "Proxy is required!";
				isValid = false;
			}

			if (!httpParams.request) {
				errorMessages.request = "Request Body is required!";
				isValid = false;
			}

			return isValid;
  }

	async function handleSubmit() {}

	function dynamicHTTPParamUpdate(id, value) {
    httpParams[id] = value;
  }

	function goBack() {
    window.location.href = "/main/tools";
  }
  </script>

	<div class="httpConfigPage">
		<div class="httpSquare">
			<h1>HTTP Tester</h1>
			<button onclick={goBack} class="back-button">Back to Tools</button>
  
			{#if acceptingParams}
			<div>
				<form class="httpParams" onsubmit="{(e) => {e.preventDefault(); handleSubmit()}}">

					{#each httpInput as param}
            {#if param.type === "select"}
              <div class="httpInputDiv">
                <label for={param.id}>{param.label}:</label>
                <select
									class="httpInput httpMethod"
                  id={param.id}
                  bind:value={httpParams[param.id]}
                  required={param.required}
                  onchange={(e) => dynamicHTTPParamUpdate(param.id, e.target.value)}
                >
                  {#each param.options as option}
                    <option value={option}>{option}</option>
                  {/each}
                </select>
              </div>
            {:else}
              <div class="httpInputDiv">
                <label for={param.id}>{param.label}:</label>
                <input
									class="httpInput"
                  id={param.id}
                  type={param.type}
                  bind:value={httpParams[param.id]}
                  placeholder={param.example}
                  required={param.required}
                  onchange={(e) => dynamicHTTPParamUpdate(param.id, e.target.value)}
                />
              </div>
            {/if}
          {/each}

					<button type="submit" title="Begins HTTP Testing with the set Parameters">Start</button>
				</form>
			</div>
    {/if}
		</div>
	</div>
  