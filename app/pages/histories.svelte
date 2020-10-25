<style>
	.container {
		text-align: center;
	}

	.history {
	}

	.preview {
		display: block;
		margin: 16px auto;
		box-shadow: 0px 0px 3px 0px rgba(0, 0, 0, 0.16);
	}
</style>

<script>
	import axios from 'axios';

	let loading = false;
	let histories = [];

	async function loadMore() {
		if (loading) return;

		loading = true;

		try {
			const response = await axios.get('/api/ocr-requests/histories');
			histories = histories.concat(response.data.histories);
		} catch (err) {
			if (err.response)
				alert(
					`Error from server! status=${err.response.status} data=${err.response.data}`
				);
			else if (err.request)
				alert(`Error! no response from server; request=${err.request}`);
			else alert(`Error! ${err.message}`);
		} finally {
			loading = false;
		}
	}

	loadMore();
</script>

<svelte:head>
	<title>OCR Project :: Histories</title>
</svelte:head>
<div class="container">
	<h2>Histories</h2>
	{#each histories as history (history.timestamp)}
		<div class="history">
			<h3>{history.timestamp}</h3>
			<img
				class="preview"
				src="{history.image}"
				alt="preview"
				width="300"
			/>
			{#if history.result.message}
				<h4>Result</h4>
				<p>{history.result.code}</p>
				<p>{history.result.message}</p>
			{:else}
				<h4>Result</h4>
				<p>{history.result.images[0].inferResult}</p>
				<p>{history.result.images[0].message}</p>
				<h5>Fields</h5>
				{#each history.result.images[0].fields as field}
					<p>
						{field.name}:
						{field.inferText}
						{Math.round(field.inferConfidence * 10000) / 100}%
					</p>
				{:else}
					<p>No field</p>
				{/each}
			{/if}
		</div>
	{/each}
	<button on:click="{loadMore}" disabled="{loading}">Load more</button>
</div>
