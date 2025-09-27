import { a as attr_class, b as attr, c as stringify, d as bind_props, f as store_get, g as ensure_array_like, u as unsubscribe_stores, h as head } from "../../chunks/index2.js";
import { Y as escape_html } from "../../chunks/context.js";
import { d as derived, w as writable } from "../../chunks/index.js";
function html(value) {
  var html2 = String(value ?? "");
  var open = "<!---->";
  return open + html2 + "<!---->";
}
function FileUpload($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let dragActive = false;
    let uploading = false;
    $$renderer2.push(`<div class="file-upload svelte-ux1wx1"><div${attr_class("drop-zone svelte-ux1wx1", void 0, { "drag-active": dragActive, "uploading": uploading })} role="button" tabindex="0">`);
    {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="upload-content svelte-ux1wx1"><div class="upload-icon svelte-ux1wx1">📁</div> <h3 class="svelte-ux1wx1">Upload Claude Transcript Files</h3> <p class="svelte-ux1wx1">Drag and drop .jsonl files here, or</p> <label for="file-input" class="upload-button svelte-ux1wx1">Choose Files</label> <input id="file-input" type="file" accept=".jsonl" multiple style="display: none;" class="svelte-ux1wx1"/> <p class="file-info svelte-ux1wx1">`);
      {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`Supports multiple .jsonl files`);
      }
      $$renderer2.push(`<!--]--></p></div>`);
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function MessageView($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let message = $$props["message"];
    function getMessageIcon(type) {
      const icons = {
        user: "🤷",
        assistant: "🤖",
        system: "⚙️",
        tool_use: "🛠️",
        tool_result: "🧰",
        thinking: "💭",
        image: "🖼️"
      };
      return icons[type] || "📄";
    }
    function isToolMessage(type) {
      return ["tool_use", "tool_result"].includes(type);
    }
    function shouldShowCollapsible(content) {
      return content.length > 500;
    }
    if (message.isSessionHeader) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="session-divider svelte-1cuch7i"></div> <div class="message session-header svelte-1cuch7i"${attr("id", `session-${stringify(message.sessionId)}`)}><div class="header svelte-1cuch7i"><span class="session-title svelte-1cuch7i">Session: ${escape_html(message.content)}</span></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div${attr_class(`message ${stringify(message.cssClass)}`, "svelte-1cuch7i")}${attr("data-message-type", message.type)}><div class="header svelte-1cuch7i"><span class="message-type svelte-1cuch7i">${escape_html(getMessageIcon(message.type))} ${escape_html(message.displayType)}</span> <div class="metadata svelte-1cuch7i"><span class="timestamp svelte-1cuch7i">${escape_html(message.formattedTimestamp)}</span> `);
      if (message.tokenUsage) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span class="token-usage svelte-1cuch7i">${escape_html(message.tokenUsage)}</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div> <div class="content svelte-1cuch7i">`);
      if (message.type === "image") {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<img${attr("src", message.content)} alt="Uploaded image" class="message-image svelte-1cuch7i"/>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (isToolMessage(message.type) && shouldShowCollapsible(message.content)) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<details class="collapsible-details svelte-1cuch7i"><summary class="svelte-1cuch7i"><div class="preview-content svelte-1cuch7i"><pre class="svelte-1cuch7i">${escape_html(message.content.substring(0, 200))}...</pre></div></summary> <div class="details-content svelte-1cuch7i"><pre class="svelte-1cuch7i">${escape_html(message.content)}</pre></div></details>`);
        } else {
          $$renderer2.push("<!--[!-->");
          if (message.contentHtml) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`${html(message.contentHtml)}`);
          } else {
            $$renderer2.push("<!--[!-->");
            $$renderer2.push(`<pre class="svelte-1cuch7i">${escape_html(message.content)}</pre>`);
          }
          $$renderer2.push(`<!--]-->`);
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]-->`);
    bind_props($$props, { message });
  });
}
const messages = writable([]);
const sessions = writable([]);
const title = writable("Claude Transcript");
const activeFilters = writable(/* @__PURE__ */ new Set([
  "user",
  "assistant",
  "sidechain",
  "system",
  "tool_use",
  "tool_result",
  "thinking",
  "image"
]));
const searchTerm = writable("");
const selectedSessionId = writable(null);
const showFilters = writable(false);
const filteredMessages = derived(
  [messages, activeFilters, searchTerm, selectedSessionId],
  ([$messages, $activeFilters, $searchTerm, $selectedSessionId]) => {
    return $messages.filter((message) => {
      if ($selectedSessionId && message.sessionId !== $selectedSessionId) {
        return false;
      }
      if (message.isSidechain) {
        if (!$activeFilters.has("sidechain") || !$activeFilters.has(message.type)) {
          return false;
        }
      } else {
        if (!$activeFilters.has(message.type)) {
          return false;
        }
      }
      if ($searchTerm) {
        const searchLower = $searchTerm.toLowerCase();
        const contentMatch = message.content.toLowerCase().includes(searchLower);
        const typeMatch = message.displayType.toLowerCase().includes(searchLower);
        if (!contentMatch && !typeMatch) {
          return false;
        }
      }
      return true;
    });
  }
);
const messageCounts = derived(
  [messages],
  ([$messages]) => {
    const counts = {
      user: 0,
      assistant: 0,
      sidechain: 0,
      system: 0,
      tool_use: 0,
      tool_result: 0,
      thinking: 0,
      image: 0
    };
    for (const message of $messages) {
      if (message.isSessionHeader) continue;
      counts[message.type] = (counts[message.type] || 0) + 1;
      if (message.isSidechain) {
        counts.sidechain = (counts.sidechain || 0) + 1;
      }
    }
    return counts;
  }
);
const visibleMessageCounts = derived(
  [filteredMessages],
  ([$filteredMessages]) => {
    const counts = {
      user: 0,
      assistant: 0,
      sidechain: 0,
      system: 0,
      tool_use: 0,
      tool_result: 0,
      thinking: 0,
      image: 0
    };
    for (const message of $filteredMessages) {
      if (message.isSessionHeader) continue;
      counts[message.type] = (counts[message.type] || 0) + 1;
      if (message.isSidechain) {
        counts.sidechain = (counts.sidechain || 0) + 1;
      }
    }
    return counts;
  }
);
function FilterToolbar($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let isFiltering;
    const filterTypes = [
      { type: "user", icon: "🤷", label: "User" },
      { type: "assistant", icon: "🤖", label: "Assistant" },
      { type: "sidechain", icon: "🔗", label: "Sub-assistant" },
      { type: "system", icon: "⚙️", label: "System" },
      { type: "tool_use", icon: "🛠️", label: "Tool Use" },
      { type: "tool_result", icon: "🧰", label: "Tool Results" },
      { type: "thinking", icon: "💭", label: "Thinking" },
      { type: "image", icon: "🖼️", label: "Images" }
    ];
    function getCountDisplay(filterType, totalCount, visibleCount, isActive) {
      if (totalCount === 0) return "(0)";
      if (isActive && visibleCount !== totalCount) {
        return `(${visibleCount}/${totalCount})`;
      }
      return `(${totalCount})`;
    }
    isFiltering = store_get($$store_subs ??= {}, "$activeFilters", activeFilters).size < filterTypes.length;
    $$renderer2.push(`<div${attr_class("filter-toolbar svelte-1mamdht", void 0, {
      "visible": store_get($$store_subs ??= {}, "$showFilters", showFilters)
    })}><div class="filter-label svelte-1mamdht"><h3 class="svelte-1mamdht">Filter:</h3></div> <div class="filter-toggles svelte-1mamdht"><!--[-->`);
    const each_array = ensure_array_like(filterTypes);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let { type, icon, label } = each_array[$$index];
      const totalCount = store_get($$store_subs ??= {}, "$messageCounts", messageCounts)[type] || 0;
      const visibleCount = store_get($$store_subs ??= {}, "$visibleMessageCounts", visibleMessageCounts)[type] || 0;
      const isActive = store_get($$store_subs ??= {}, "$activeFilters", activeFilters).has(type);
      if (totalCount > 0) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<button${attr_class("filter-toggle svelte-1mamdht", void 0, { "active": isActive })}${attr("data-type", type)}>${escape_html(icon)} ${escape_html(label)} <span class="count svelte-1mamdht">${escape_html(getCountDisplay(type, totalCount, visibleCount, isFiltering))}</span></button>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div> <div class="filter-actions svelte-1mamdht"><button class="filter-action-btn svelte-1mamdht">All</button> <button class="filter-action-btn svelte-1mamdht">None</button> <button class="filter-action-btn close-btn svelte-1mamdht" title="Close filters">✕</button></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let hasData = false;
    hasData = store_get($$store_subs ??= {}, "$messages", messages).length > 0;
    head($$renderer2, ($$renderer3) => {
      $$renderer3.title(($$renderer4) => {
        $$renderer4.push(`<title>${escape_html(store_get($$store_subs ??= {}, "$title", title))} - Claude Code Log Viewer</title>`);
      });
    });
    $$renderer2.push(`<div class="app svelte-1uha8ag">`);
    FilterToolbar($$renderer2);
    $$renderer2.push(`<!----> <main${attr_class("main-content svelte-1uha8ag", void 0, { "with-data": hasData })}><header class="app-header svelte-1uha8ag"><h1 class="svelte-1uha8ag">Claude Code Log Viewer</h1> `);
    if (hasData) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="header-actions svelte-1uha8ag"><button class="action-btn svelte-1uha8ag">🗑️ Clear Data</button> <button class="action-btn svelte-1uha8ag">🔍 ${escape_html(store_get($$store_subs ??= {}, "$showFilters", showFilters) ? "Hide" : "Show")} Filters</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></header> `);
    if (!hasData) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="welcome-section svelte-1uha8ag"><div class="welcome-content svelte-1uha8ag"><h2 class="svelte-1uha8ag">Welcome to Claude Code Log Viewer</h2> <p class="svelte-1uha8ag">Upload your Claude Code transcript files (.jsonl) to view them in an interactive format.</p></div> `);
      FileUpload($$renderer2);
      $$renderer2.push(`<!----></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="transcript-viewer svelte-1uha8ag"><div class="transcript-header svelte-1uha8ag"><h2 class="svelte-1uha8ag">${escape_html(store_get($$store_subs ??= {}, "$title", title))}</h2> <div class="transcript-stats svelte-1uha8ag"><span>${escape_html(store_get($$store_subs ??= {}, "$sessions", sessions).length)} session${escape_html(store_get($$store_subs ??= {}, "$sessions", sessions).length === 1 ? "" : "s")}</span> <span>•</span> <span>${escape_html(store_get($$store_subs ??= {}, "$messages", messages).filter((m) => !m.isSessionHeader).length)} message${escape_html(store_get($$store_subs ??= {}, "$messages", messages).filter((m) => !m.isSessionHeader).length === 1 ? "" : "s")}</span> `);
      if (store_get($$store_subs ??= {}, "$filteredMessages", filteredMessages).length !== store_get($$store_subs ??= {}, "$messages", messages).filter((m) => !m.isSessionHeader).length) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<span>•</span> <span class="filtered-count svelte-1uha8ag">${escape_html(store_get($$store_subs ??= {}, "$filteredMessages", filteredMessages).filter((m) => !m.isSessionHeader).length)} visible</span>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div></div> `);
      if (store_get($$store_subs ??= {}, "$sessions", sessions).length > 1) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="session-nav svelte-1uha8ag"><h3 class="svelte-1uha8ag">Sessions</h3> <div class="session-list svelte-1uha8ag"><!--[-->`);
        const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$sessions", sessions));
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let session = each_array[$$index];
          $$renderer2.push(`<div class="session-item svelte-1uha8ag"><div class="session-summary svelte-1uha8ag">${escape_html(session.summary || `Session ${session.id.substring(0, 8)}`)}</div> <div class="session-meta svelte-1uha8ag"><span class="session-messages">${escape_html(session.messageCount)} messages</span> <span class="session-time">${escape_html(session.timestampRange)}</span></div> `);
          if (session.tokenSummary) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="session-tokens svelte-1uha8ag">${escape_html(session.tokenSummary)}</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></div>`);
        }
        $$renderer2.push(`<!--]--></div></div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--> <div class="messages-container svelte-1uha8ag"><!--[-->`);
      const each_array_1 = ensure_array_like(store_get($$store_subs ??= {}, "$filteredMessages", filteredMessages));
      for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
        let message = each_array_1[$$index_1];
        MessageView($$renderer2, { message });
      }
      $$renderer2.push(`<!--]--></div></div>`);
    }
    $$renderer2.push(`<!--]--></main> `);
    if (hasData) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="floating-actions svelte-1uha8ag"><button class="floating-btn svelte-1uha8ag" title="Toggle filters">🔍</button> <button class="floating-btn svelte-1uha8ag" title="Scroll to top">🔝</button></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
  });
}
export {
  _page as default
};
