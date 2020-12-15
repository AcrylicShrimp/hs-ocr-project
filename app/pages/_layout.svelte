<style>
	.container {
		margin: 0 auto;
		padding: 8px;
		max-width: 900px;
	}

	.content-container {
		min-height: 600px;
	}
</style>

<script>
	import Header from '../components/Header';
	import Footer from '../components/Footer';
</script>

<div class="container">
	<Header />
	<div class="content-container">
		<slot />
	</div>
	<Footer />
</div>
