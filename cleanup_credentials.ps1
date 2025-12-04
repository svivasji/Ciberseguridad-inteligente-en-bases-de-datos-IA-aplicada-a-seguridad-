# Script para limpiar credenciales de `config.py` del historial git
# Ejecuta estos comandos en PowerShell desde la raíz del repositorio

# PASO 1: Guardar una copia de config.py con las credenciales actuales (si lo necesitas después)
Write-Host "1. Haciendo backup de config.py actual..." -ForegroundColor Green
Copy-Item "src/config.py" "src/config.py.backup" -Force
Write-Host "   Backup guardado en src/config.py.backup"
Write-Host ""

# PASO 2: Reemplazar config.py con config_example.py (copia segura sin credenciales)
Write-Host "2. Reemplazando src/config.py con src/config_example.py..." -ForegroundColor Green
Copy-Item "src/config_example.py" "src/config.py" -Force
Write-Host "   Ahora src/config.py contiene solo la plantilla sin credenciales"
Write-Host ""

# PASO 3: Verificar que .gitignore contiene config.py
Write-Host "3. Verificando que .gitignore contiene 'config.py'..." -ForegroundColor Green
$gitignore_content = Get-Content ".gitignore" -Raw
if ($gitignore_content -match "config\.py") {
    Write-Host "   ✓ config.py ya está en .gitignore"
} else {
    Write-Host "   ✗ config.py NO está en .gitignore. Añadiendo..."
    Add-Content ".gitignore" "config.py"
    Write-Host "   ✓ Añadido config.py a .gitignore"
}
Write-Host ""

# PASO 4: Remover config.py del índice de git (para que git no lo siga)
Write-Host "4. Removiendo config.py del índice de git..." -ForegroundColor Green
git rm --cached "src/config.py" 2>$null
Write-Host "   ✓ config.py removido del índice de git"
Write-Host ""

# PASO 5: (OPCIONAL) Usar git filter-repo para limpiar el historial
Write-Host "5. Opción A: Limpiar config.py del historial completo de git (DESTRUCTIVO)" -ForegroundColor Yellow
Write-Host "   Este paso requiere tener git-filter-repo instalado:"
Write-Host "   pip install git-filter-repo"
Write-Host ""
Write-Host "   Si quieres proceder, ejecuta (no recomendado si ya hay PRs abiertas):" -ForegroundColor Cyan
Write-Host "   git filter-repo --path src/config.py --invert-paths"
Write-Host ""
Write-Host "   O más seguro, acepta que está en el historial pero no se vuelva a comitear:" -ForegroundColor Cyan
Write-Host "   (Salta este paso)"
Write-Host ""

# PASO 6: Confirmar los cambios
Write-Host "6. Confirmando cambios en git..." -ForegroundColor Green
git add ".gitignore"
git add -u  # Remove deleted files
Write-Host "   ✓ Cambios staged"
Write-Host ""

# PASO 7: Crear commit
Write-Host "7. Creando commit..." -ForegroundColor Green
git commit -m "Add config_example.py and remove config.py from tracking

- Replace config.py with template (config_example.py)
- Ensure config.py is in .gitignore to prevent future credential leaks
- Backup of original config.py saved as src/config.py.backup (delete manually if not needed)

Note: config.py still exists in git history. To completely remove it:
  pip install git-filter-repo
  git filter-repo --path src/config.py --invert-paths
  git push origin --force-with-lease

For now, future commits will not include config.py changes."

Write-Host "   ✓ Commit creado"
Write-Host ""

# PASO 8: Instrucciones finales
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ PROCESO COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Edita src/config.py con tus credenciales reales (NO se subirán a git)"
Write-Host "2. Prueba la app: cd web && python app.py"
Write-Host "3. Si quieres limpiar completamente el historial de config.py, ejecuta:"
Write-Host "   pip install git-filter-repo"
Write-Host "   git filter-repo --path src/config.py --invert-paths"
Write-Host "   git push origin --force-with-lease"
Write-Host ""
Write-Host "⚠️  ADVERTENCIA: git filter-repo modifica el historial. Solo hazlo si:"
Write-Host "   - No hay colaboradores con commits basados en la rama actual"
Write-Host "   - No hay PRs abiertas"
Write-Host ""
Write-Host "Puedes deletear src/config.py.backup después de confirmar que todo funciona."
