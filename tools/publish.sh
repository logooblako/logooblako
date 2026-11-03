#!/bin/zsh
# Публикация сайта на GitHub Pages (запускать после: .bin/gh auth login --web)
set -e
cd "$(dirname "$0")/.."
GH=./.bin/gh
USER=$($GH api user -q .login)
git add -A && git -c user.name="Логооблако" -c user.email="noreply@logooblako.local" commit -q -m "Обновление сайта" || true
if ! $GH repo view "$USER/logooblako" >/dev/null 2>&1; then
  $GH repo create logooblako --public --source . --remote origin --push --description "Логооблако — логопедия для родителей"
else
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$USER/logooblako.git"
  $GH auth setup-git; git push -u origin main
fi
$GH api -X POST "repos/$USER/logooblako/pages" -f build_type=workflow >/dev/null 2>&1 || $GH api -X PUT "repos/$USER/logooblako/pages" -f build_type=workflow >/dev/null 2>&1 || true
$GH workflow run pages.yml -R "$USER/logooblako" >/dev/null 2>&1 || true
echo "Адрес сайта: https://$USER.github.io/logooblako/"
