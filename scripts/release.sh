#!/bin/bash

set -e

if [ $# -eq 0 ]; then
    echo "Missing flag. Use --minor, --major or --patch"
    exit 1
fi

BRANCH="production-release"

git fetch origin && \
git fetch origin -t && \
git checkout -b "$BRANCH" origin/main && \

echo "Fetched origin, created release-branch."

NEW_TAG_D="-1"
NEW_TAG=$NEW_TAG_D

for cmd in "$@"
do
	case $cmd in
		"--major")
			echo "Incrementing Major Version"
      NEW_TAG=$(./semver.sh -v major)
			;;
		"--minor")
			echo "Incrementing Minor Version"
      NEW_TAG=$(./semver.sh -v minor)
			;;
		"--patch")
			echo "Incrementing Patch Version"
      NEW_TAG=$(./semver.sh -v patch)
			;;
        *)
            echo "No version specified"
            ;;
	esac
done

if [ $NEW_TAG == $NEW_TAG_D ]; then
exit 1
fi

RELEASE_BRANCH="${BRANCH}-v${NEW_TAG}" && \

echo "Creating branch $RELEASE_BRANCH" && \
git branch -m "$RELEASE_BRANCH" && \

echo "New tag $NEW_TAG" && \
git tag -a "$NEW_TAG" -m "Production ${NEW_TAG}" && \

echo "Pushing branch $RELEASE_BRANCH" && \
git push origin --follow-tags "$RELEASE_BRANCH" && \

echo "Don't forget to merge to main and Approve the deploy to the production environment!"

exit 0
