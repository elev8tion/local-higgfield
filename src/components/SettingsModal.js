import { getApiBaseUrl, listJobTypes } from '../lib/localapi.js';
import { getCachedBackendModelCatalog, loadBackendModelCatalog } from '../lib/modelCatalog.js';

export function SettingsModal(onClose) {
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 bg-black/80 flex items-center justify-center z-50';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.right = '0';
    overlay.style.bottom = '0';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = '100';

    const modal = document.createElement('div');
    modal.className = 'bg-card p-6 rounded-xl border border-border-color w-[28rem] glass';
    modal.style.background = 'var(--bg-card)';
    modal.style.padding = '1.5rem';
    modal.style.borderRadius = 'var(--border-radius-xl)';
    modal.style.border = '1px solid var(--border-color)';
    modal.style.width = '28rem';

    const title = document.createElement('h2');
    title.textContent = 'Local Runtime';
    title.className = 'text-xl font-bold mb-4';
    title.style.marginBottom = '1rem';

    const intro = document.createElement('p');
    intro.className = 'text-sm text-secondary mb-4';
    intro.textContent = 'This build is configured for local use. No sign-in or external API key is required.';

    const details = document.createElement('div');
    details.className = 'space-y-3 mb-5 text-sm';
    details.innerHTML = `
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div class="text-[10px] uppercase tracking-widest text-muted mb-1">Backend URL</div>
            <div class="font-mono text-white break-all">${getApiBaseUrl()}</div>
        </div>
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div class="text-[10px] uppercase tracking-widest text-muted mb-1">Mode</div>
            <div class="text-white">Local control plane with backend job pipeline</div>
        </div>
    `;

    const jobTypesCard = document.createElement('div');
    jobTypesCard.className = 'rounded-2xl border border-white/10 bg-white/5 p-4 mb-5';
    jobTypesCard.innerHTML = `
        <div class="text-[10px] uppercase tracking-widest text-muted mb-2">Registered Job Types</div>
        <div class="job-types text-sm text-secondary">Loading…</div>
    `;

    const jobTypesEl = jobTypesCard.querySelector('.job-types');

    const modelsCard = document.createElement('div');
    modelsCard.className = 'rounded-2xl border border-white/10 bg-white/5 p-4 mb-5';
    modelsCard.innerHTML = `
        <div class="text-[10px] uppercase tracking-widest text-muted mb-2">Backend Model Catalog</div>
        <div class="model-catalog text-sm text-secondary">Loading…</div>
    `;

    const modelsEl = modelsCard.querySelector('.model-catalog');

    const btnContainer = document.createElement('div');
    btnContainer.className = 'flex justify-end gap-2';
    btnContainer.style.display = 'flex';
    btnContainer.style.justifyContent = 'flex-end';
    btnContainer.style.gap = '0.5rem';

    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close';
    closeBtn.className = 'px-4 py-2 rounded hover:bg-white/5';
    closeBtn.onclick = () => {
        document.body.removeChild(overlay);
        if (onClose) onClose();
    };

    modal.appendChild(title);
    modal.appendChild(intro);
    modal.appendChild(details);
    modal.appendChild(jobTypesCard);
    modal.appendChild(modelsCard);

    btnContainer.appendChild(closeBtn);
    modal.appendChild(btnContainer);

    overlay.appendChild(modal);

    listJobTypes()
        .then(({ job_types }) => {
            if (!job_types?.length) {
                jobTypesEl.textContent = 'No job types registered.';
                return;
            }
            jobTypesEl.innerHTML = job_types
                .map((item) => {
                    const status = item.implemented ? 'implemented' : 'planned';
                    return `<div class="flex items-center justify-between gap-3 py-1.5 border-b border-white/5 last:border-b-0">
                        <span class="font-mono text-white">${item.type}</span>
                        <span class="text-[10px] uppercase tracking-widest ${item.implemented ? 'text-primary' : 'text-muted'}">${status}</span>
                    </div>`;
                })
                .join('');
        })
        .catch(() => {
            jobTypesEl.textContent = 'Unable to load backend job types.';
        });

    const renderCatalog = (catalog) => {
        const models = catalog?.models || [];
        if (!models.length) {
            modelsEl.textContent = 'No backend model metadata available yet.';
            return;
        }
        modelsEl.innerHTML = models
            .map((model) => {
                const runtimeLabel = model?.runtime?.configured
                    ? model.runtime.mode
                    : model?.runtime?.placeholder_fallback
                        ? `${model.runtime.mode} fallback`
                        : model?.runtime?.mode || 'unknown';
                return `<div class="py-2 border-b border-white/5 last:border-b-0">
                    <div class="flex items-center justify-between gap-3">
                        <span class="text-white">${model.name}</span>
                        <span class="text-[10px] uppercase tracking-widest ${model.implemented ? 'text-primary' : 'text-muted'}">${model.job_type}</span>
                    </div>
                    <div class="text-[10px] uppercase tracking-widest text-muted mt-1">${runtimeLabel}</div>
                </div>`;
            })
            .join('');
    };

    const cachedCatalog = getCachedBackendModelCatalog();
    if (cachedCatalog) {
        renderCatalog(cachedCatalog);
    } else {
        loadBackendModelCatalog()
            .then(renderCatalog)
            .catch(() => {
                modelsEl.textContent = 'Unable to load backend model metadata.';
            });
    }

    // Close on outside click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
            if (onClose) onClose();
        }
    });

    return overlay;
}
