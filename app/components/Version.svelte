<script>
	import axios from 'axios';
</script>

<span>
	{#await axios.get('/api/version')}
		Fetching...
	{:then version}
		{version.data}
	{:catch}
		N/A
	{/await}
</span>
