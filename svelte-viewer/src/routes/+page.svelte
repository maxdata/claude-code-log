<script lang="ts">
	import { onMount } from 'svelte';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import MessageView from '$lib/components/MessageView.svelte';
	import FilterToolbar from '$lib/components/FilterToolbar.svelte';
	import { 
		messages, 
		sessions, 
		title, 
		isLoading,
		filteredMessages,
		showFilters,
		loadTranscriptData,
		clearTranscriptData
	} from '$lib/stores/transcript.ts';
	import type { TranscriptData } from '$lib/types.ts';

	let hasData = false;

	function handleUploadSuccess(event: CustomEvent<TranscriptData>) {
		const data = event.detail;
		loadTranscriptData(data);
		hasData = true;
	}

	function handleUploadError(event: CustomEvent<string>) {
		console.error('Upload failed:', event.detail);
		// You could show a toast notification here
	}

	function handleClearData() {
		clearTranscriptData();
		hasData = false;
	}

	function toggleFilters() {
		showFilters.update(show => !show);
	}

	function scrollToTop() {
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	// Track if we have any data loaded
	$: hasData = $messages.length > 0;
</script>

<svelte:head>
	<title>{$title} - Claude Code Log Viewer</title>
</svelte:head>

<div class="app">
	<FilterToolbar />
	
	<main class="main-content" class:with-data={hasData}>
		<header class="app-header">
			<h1>Claude Code Log Viewer</h1>
			{#if hasData}
				<div class="header-actions">
					<button class="action-btn" on:click={handleClearData}>
						🗑️ Clear Data
					</button>
					<button class="action-btn" on:click={toggleFilters}>
						🔍 {$showFilters ? 'Hide' : 'Show'} Filters
					</button>
				</div>
			{/if}
		</header>

		{#if !hasData}
			<div class="welcome-section">
				<div class="welcome-content">
					<h2>Welcome to Claude Code Log Viewer</h2>
					<p>Upload your Claude Code transcript files (.jsonl) to view them in an interactive format.</p>
				</div>
				<FileUpload on:success={handleUploadSuccess} on:error={handleUploadError} />
			</div>
		{:else}
			<div class="transcript-viewer">
				<div class="transcript-header">
					<h2>{$title}</h2>
					<div class="transcript-stats">
						<span>{$sessions.length} session{$sessions.length === 1 ? '' : 's'}</span>
						<span>•</span>
						<span>{$messages.filter(m => !m.isSessionHeader).length} message{$messages.filter(m => !m.isSessionHeader).length === 1 ? '' : 's'}</span>
						{#if $filteredMessages.length !== $messages.filter(m => !m.isSessionHeader).length}
							<span>•</span>
							<span class="filtered-count">
								{$filteredMessages.filter(m => !m.isSessionHeader).length} visible
							</span>
						{/if}
					</div>
				</div>

				{#if $sessions.length > 1}
					<div class="session-nav">
						<h3>Sessions</h3>
						<div class="session-list">
							{#each $sessions as session}
								<div class="session-item">
									<div class="session-summary">
										{session.summary || `Session ${session.id.substring(0, 8)}`}
									</div>
									<div class="session-meta">
										<span class="session-messages">{session.messageCount} messages</span>
										<span class="session-time">{session.timestampRange}</span>
									</div>
									{#if session.tokenSummary}
										<div class="session-tokens">{session.tokenSummary}</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<div class="messages-container">
					{#each $filteredMessages as message (message.id)}
						<MessageView {message} />
					{/each}
				</div>
			</div>
		{/if}
	</main>

	{#if hasData}
		<div class="floating-actions">
			<button class="floating-btn" on:click={toggleFilters} title="Toggle filters">
				🔍
			</button>
			<button class="floating-btn" on:click={scrollToTop} title="Scroll to top">
				🔝
			</button>
		</div>
	{/if}
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
			Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
		line-height: 1.5;
		color: #333;
		background: #f8f9fa;
	}

	:global(*) {
		box-sizing: border-box;
	}

	.app {
		min-height: 100vh;
	}

	.main-content {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
		transition: padding-top 0.3s ease;
	}

	.main-content.with-data {
		padding-top: 1rem;
	}

	.app-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
		gap: 1rem;
	}

	.app-header h1 {
		margin: 0;
		color: #2c3e50;
		font-size: 2rem;
		font-weight: 600;
	}

	.header-actions {
		display: flex;
		gap: 0.75rem;
	}

	.action-btn {
		padding: 0.5rem 1rem;
		border: 1px solid #dee2e6;
		border-radius: 6px;
		background: white;
		color: #495057;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.action-btn:hover {
		background: #e9ecef;
		border-color: #adb5bd;
	}

	.welcome-section {
		text-align: center;
		padding: 4rem 0;
	}

	.welcome-content {
		margin-bottom: 3rem;
	}

	.welcome-content h2 {
		color: #2c3e50;
		font-size: 2.5rem;
		margin-bottom: 1rem;
		font-weight: 300;
	}

	.welcome-content p {
		font-size: 1.2rem;
		color: #666;
		max-width: 600px;
		margin: 0 auto;
	}

	.transcript-viewer {
		background: white;
		border-radius: 8px;
		box-shadow: 0 2px 10px rgba(0,0,0,0.1);
		overflow: hidden;
	}

	.transcript-header {
		padding: 1.5rem 2rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}

	.transcript-header h2 {
		margin: 0 0 0.5rem 0;
		font-size: 1.75rem;
		font-weight: 600;
	}

	.transcript-stats {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.95rem;
		opacity: 0.9;
	}

	.filtered-count {
		color: #ffd700;
		font-weight: 500;
	}

	.session-nav {
		padding: 1.5rem 2rem;
		border-bottom: 1px solid #e9ecef;
		background: #f8f9fa;
	}

	.session-nav h3 {
		margin: 0 0 1rem 0;
		color: #495057;
		font-size: 1.25rem;
	}

	.session-list {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
		gap: 1rem;
	}

	.session-item {
		padding: 1rem;
		background: white;
		border-radius: 6px;
		border: 1px solid #e9ecef;
		transition: all 0.2s ease;
	}

	.session-item:hover {
		border-color: #007acc;
		box-shadow: 0 2px 8px rgba(0,122,204,0.1);
	}

	.session-summary {
		font-weight: 600;
		color: #2c3e50;
		margin-bottom: 0.5rem;
	}

	.session-meta {
		display: flex;
		gap: 1rem;
		color: #6c757d;
		font-size: 0.9rem;
		margin-bottom: 0.25rem;
	}

	.session-tokens {
		color: #6c757d;
		font-size: 0.8rem;
		font-style: italic;
	}

	.messages-container {
		padding: 2rem;
	}

	.floating-actions {
		position: fixed;
		bottom: 2rem;
		right: 2rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		z-index: 100;
	}

	.floating-btn {
		width: 3rem;
		height: 3rem;
		border: none;
		border-radius: 50%;
		background: #007acc;
		color: white;
		font-size: 1.2rem;
		cursor: pointer;
		box-shadow: 0 4px 12px rgba(0,122,204,0.3);
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.floating-btn:hover {
		background: #005a9f;
		transform: translateY(-2px);
		box-shadow: 0 6px 16px rgba(0,122,204,0.4);
	}

	@media (max-width: 768px) {
		.main-content {
			padding: 1rem;
		}

		.app-header {
			flex-direction: column;
			align-items: stretch;
			text-align: center;
		}

		.header-actions {
			justify-content: center;
		}

		.welcome-content h2 {
			font-size: 2rem;
		}

		.transcript-header {
			padding: 1rem;
		}

		.session-nav {
			padding: 1rem;
		}

		.messages-container {
			padding: 1rem;
		}

		.floating-actions {
			bottom: 1rem;
			right: 1rem;
		}
	}
</style>