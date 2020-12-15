<style>
	.container {
		text-align: center;
	}

	.preview {
		display: block;
		margin: 16px auto;
		box-shadow: 0px 0px 3px 0px rgba(0, 0, 0, 0.16);
	}

	.preview-container {
		display: flex;
		flex-direction: row;
		align-items: flex-start;
		justify-content: center;
	}

	.preview-inner-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-start;
	}

	.final-text {
		background-color: #bcbcbc;
		white-space: pre-line;
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
		<div>
			<h3>{history.timestamp}</h3>
			<img
				class="preview"
				src="{history.image}"
				alt="preview"
				width="500"
			/>
			<h4>Result</h4>
			<h5>Images</h5>
			<div class="preview-container">
				<div class="preview-inner-container">
					<span>Gray</span>
					<img
						class="preview"
						src="{history.grayImage}"
						alt="preview"
						width="250"
					/>
				</div>
				<div class="preview-inner-container">
					<span>Binary</span>
					{#if history.binaryImage}
						<img
							class="preview"
							src="{history.binaryImage}"
							alt="preview"
							width="250"
						/>
					{:else}<span class="preview-text">N/A</span>{/if}
				</div>
				<div class="preview-inner-container">
					<span>Drawn</span>
					<img
						class="preview"
						src="{history.drawnImage}"
						alt="preview"
						width="250"
					/>
				</div>
			</div>
			<div class="preview-inner-container">
				<span>Processed</span>
				<img
					class="preview"
					src="{history.processedImage}"
					alt="preview"
					width="500"
				/>
			</div>
			<h5>Texts</h5>
			{#each history.result.texts as text}
				<p>
					<span class="final-text">{text.text}</span>
					(confidence:
					{Math.round(text.confidence * 10000) / 100}%)
				</p>
			{:else}
				<p>No field</p>
			{/each}
		</div>
	{/each}
	<button on:click="{loadMore}" disabled="{loading}">Load more</button>
</div>
