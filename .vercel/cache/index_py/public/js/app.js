document.addEventListener('DOMContentLoaded', () => {
    const userBadge = document.getElementById('userBadge');
    if (userBadge) {
        userBadge.innerText = `[ ID: ${localStorage.getItem('usuario_id')} ] ${localStorage.getItem('usuario_nombre')}`;
    }

    if (document.getElementById('ledger-list')) {
        cargarDocumentos();
    }

    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btnSubmit = uploadForm.querySelector('button[type="submit"]');
            const originalText = btnSubmit.innerHTML;
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Procesando...';

            const archivoInput = document.getElementById('archivo');
            const categoriaSelect = document.getElementById('categoria');
            const usuario_id = localStorage.getItem('usuario_id');

            const formData = new FormData();
            formData.append('file', archivoInput.files[0]);
            formData.append('categoria', categoriaSelect.value);
            formData.append('usuario_id', usuario_id);

            try {
                const res = await fetch('/api/subir', { method: 'POST', body: formData });
                const resultado = await res.json();

                if (resultado.status === 'success') {
                    alert(`✅ ¡BLOQUE ESTAMPADO EN EL LEDGER!\n\nSHA-256 Generado:\n${resultado.hash}`);
                    uploadForm.reset();
                    cargarDocumentos();
                } else {
                    alert(`❌ Error del Nodo: ${resultado.message}`);
                }
            } catch (err) {
                alert("❌ Fallo de conexión con Vercel.");
            } finally {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = originalText;
            }
        });
    }
});

async function cargarDocumentos() {
    const usuario_id = localStorage.getItem('usuario_id');
    const container = document.getElementById('ledger-list');
    
    if (!container) return;
    container.innerHTML = `<div class="text-center py-10 text-cyan-400 text-sm"><i class="fa-solid fa-circle-notch animate-spin mr-2 text-2xl"></i><br><br>Sincronizando con Supabase...</div>`;

    try {
        const res = await fetch(`/api/documentos/${usuario_id}`);
        const data = await res.json();

        // Validar si el backend mandó un error literal
        if (data.error_real) {
            container.innerHTML = `<p class="text-sm text-red-400 text-center font-mono bg-red-900/20 p-4 rounded-lg border border-red-500/30">Fallo en DB: ${data.error_real}</p>`;
            return;
        }

        if (!Array.isArray(data) || data.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 bg-slate-800/30 rounded-xl border border-dashed border-slate-600">
                    <i class="fa-solid fa-box-open text-5xl text-slate-600 mb-4"></i>
                    <p class="text-sm font-bold text-slate-400">Bóveda vacía.</p>
                    <p class="text-xs text-slate-500 mt-1">Aún no tienes bloques minados en tu cuenta.</p>
                </div>`;
            return;
        }

        container.innerHTML = data.map(doc => {
            const esImagen = doc.nombre_archivo.toLowerCase().match(/\.(jpeg|jpg|gif|png)$/) != null;
            const icono = esImagen ? 'fa-image text-emerald-400' : 'fa-file-pdf text-rose-400';

            return `
            <div class="bg-slate-800/60 p-5 rounded-xl border border-slate-700 flex flex-col sm:flex-row justify-between sm:items-center gap-4 hover:border-cyan-500/50 transition duration-300 hover:shadow-[0_0_15px_rgba(6,182,212,0.15)] group">
                <div>
                    <h4 class="font-bold text-slate-200 text-sm flex items-center">
                        <i class="fa-solid ${icono} mr-3 text-lg"></i> ${doc.nombre_archivo}
                    </h4>
                    <p class="text-xs font-mono text-slate-400 mt-2 pl-7 border-l-2 border-slate-600 ml-2">
                        <span class="text-cyan-400 font-bold">${doc.categoria}</span>
                    </p>
                </div>
                <div class="sm:text-right flex flex-col items-end">
                    <span class="inline-block text-[10px] font-mono font-bold text-cyan-300 bg-cyan-900/40 border border-cyan-700/50 px-2.5 py-1.5 rounded uppercase tracking-wider">
                        <i class="fa-solid fa-fingerprint mr-1 opacity-70"></i> ${doc.sha256_hash.substring(0, 16)}...
                    </span>
                    <a href="${doc.url_storage}" target="_blank" class="block text-xs font-bold text-slate-400 group-hover:text-cyan-400 transition mt-3 bg-slate-900 px-3 py-1.5 rounded border border-slate-700 hover:border-cyan-500">
                        <i class="fa-solid fa-eye mr-1"></i> Abrir Documento Original
                    </a>
                </div>
            </div>`;
        }).join('');
    } catch (error) {
        container.innerHTML = `<p class="text-sm text-red-400 text-center font-bold bg-red-900/20 p-4 rounded-lg">Error crítico al conectar con Vercel. Revisa la consola.</p>`;
    }
}

function cerrarSesion() {
    localStorage.clear();
    window.location.replace('login.html');
} 
