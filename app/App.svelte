<script>
	import { Router, afterPageLoad } from '@sveltech/routify';

	import { routes } from './.routify/routes';

	$afterPageLoad(() => window.scrollTo(0, 0));
</script>

<Router routes="{routes}" />
