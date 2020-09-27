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
</style>

<script>
	import axios from 'axios';

	let image;
	let src;
	let uploading = false;
	let result;

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

			const response = await axios.post('/api/ocr-requests', formData);

			console.log(response.data);

			result = response.data;
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
		accept="image/png,image/jpg"
		on:change="{(event) => (image = event.target.files[0])}"
	/>
	{#if image}
		<img class="preview" alt="{image.name}" src="{src}" width="300" />
	{/if}
	<button on:click="{handleClick}">Run OCR</button>
	{#if uploading}
		<h2>Running OCR...</h2>
	{:else if result}
		{#if result.message}
			<h2>Result</h2>
			<p>{result.code}</p>
			<p>{result.message}</p>
		{:else}
			<h2>Result</h2>
			<p>{result.images[0].inferResult}</p>
			<p>{result.images[0].message}</p>
			<h3>Fields</h3>
			{#each result.images[0].fields as field}
				<p>
					{field.name}: {field.inferText}
					{Math.round(field.inferConfidence * 10000) / 100}%
				</p>
			{/each}
		{/if}
	{/if}
</div>
