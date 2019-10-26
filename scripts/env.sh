export ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
export GIT_BRANCH=$(echo $CODEBUILD_WEBHOOK_BASE_REF | cut -d'/' -f 3)
if [ "$GIT_BRANCH" == "master" ]; then
  export GIT_BRANCH="prod"
fi
export BUCKET="coffeepot-$GIT_BRANCH-bucket-$ACCOUNT_ID"