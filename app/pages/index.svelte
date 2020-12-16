<style>
	.container {
		text-align: center;
	}

	.label {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		margin: 16px auto;
		border: none;
		border-radius: 4px;
		padding: 4px;
		max-width: 300px;
		height: 70px;
		background-color: transparent;
		font-size: 18px;
		color: black;
		cursor: pointer;
		outline: none;
		box-shadow: 0px 0px 3px 0px rgba(0, 0, 0, 0.16);
		transition: color 0.2s, box-shadow 0.2s;
	}

	.input {
		display: none;
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

	.preview-text {
		width: 250px;
	}

	.button-container {
		margin: 19px 0;
	}

	.final-text {
		background-color: #bcbcbc;
		white-space: pre-line;
	}
</style>

<script>
	import axios from 'axios';

	let image;
	let src;
	let uploading = false;
	let result;
	let resultGrayImage;
	let resultBinaryImage;
	let resultDrawnImage;
	let resultProcessedImage;

	$: {
		if (image) {
			const reader = new FileReader();

			reader.onload = (event) => (src = event.target.result);
			reader.readAsDataURL(image);
		}
	}

	async function handleClick() {
		if (uploading) return;

		uploading = true;

		try {
			const formData = new FormData();
			formData.append('image', image);
			formData.append(
				'type',
				image.name.endsWith('.png') ? 'png' : 'jpg'
			);
			formData.append(
				'api',
				document.getElementById('api-naver').checked
					? 'naver'
					: 'google'
			);
			formData.append(
				'preprocess',
				document.getElementById('preprocess').checked ? 'yes' : 'no'
			);

			const response = await axios.post('/api/ocr-requests', formData);
			result = JSON.parse(response.data.result);

			console.log(result);

			resultGrayImage = response.data.grayImage;
			resultBinaryImage = response.data.binaryImage;
			resultDrawnImage = response.data.drawnImage;
			resultProcessedImage = response.data.processedImage;
		} catch (err) {
			if (err.response)
				alert(
					`Error from server! status=${err.response.status} data=${err.response.data}`
				);
			else if (err.request)
				alert(`Error! no response from server; request=${err.request}`);
			else alert(`Error! ${err.message}`);
		} finally {
			uploading = false;
		}
	}
</script>

<svelte:head>
	<title>OCR Project</title>
</svelte:head>
<div class="container">
	<h2>Upload image</h2>
	<label for="image-upload" class="label">Click here to select image</label>
	<input
		id="image-upload"
		type="file"
		class="input"
		accept="image/png,image/jpeg"
		on:change="{(event) => (image = event.target.files[0])}"
	/>
	{#if image}
		<img class="preview" alt="{image.name}" src="{src}" width="300" />
	{/if}
	<div class="button-container">
		<input id="api-naver" name="api" type="radio" value="naver" checked />
		<label for="api-naver">Use Naver OCR</label>
	</div>
	<div class="button-container">
		<input id="api-google" name="api" type="radio" value="google" />
		<label for="api-google">Use Google OCR</label>
	</div>
	<div class="button-container">
		<input id="preprocess" type="checkbox" checked />
		<label for="preprocess">Enable preprocess</label>
	</div>
	<button on:click="{handleClick}">Run OCR</button>
	{#if uploading}
		<h2>Running OCR...</h2>
	{:else if result}
		<h2>Result</h2>
		<h3>Images</h3>
		<div class="preview-container">
			<div class="preview-inner-container">
				<h4>Gray</h4>
				{#if resultGrayImage}
					<img
						class="preview"
						src="{resultGrayImage}"
						alt="preview"
						width="250"
					/>
				{:else}<span class="preview-text">N/A</span>{/if}
			</div>
			<div class="preview-inner-container">
				<h4>Binary</h4>
				{#if resultBinaryImage}
					<img
						class="preview"
						src="{resultBinaryImage}"
						alt="preview"
						width="250"
					/>
				{:else}<span class="preview-text">N/A</span>{/if}
			</div>
			<div class="preview-inner-container">
				<h4>Drawn</h4>
				{#if resultDrawnImage}
					<img
						class="preview"
						src="{resultDrawnImage}"
						alt="preview"
						width="250"
					/>
				{:else}<span class="preview-text">N/A</span>{/if}
			</div>
		</div>
		<div class="preview-inner-container">
			<h4>Processed</h4>
			{#if resultProcessedImage}
				<img
					class="preview"
					src="{resultProcessedImage}"
					alt="preview"
					width="500"
				/>
			{:else}<span class="preview-text">N/A</span>{/if}
		</div>
		<h3>Texts</h3>
		{#each result.texts as text}
			<p>
				<span class="final-text">{text.text}</span>
				(confidence:
				{Math.round(text.confidence * 10000) / 100}%)
			</p>
		{:else}
			<p>No field</p>
		{/each}
	{/if}
</div>
