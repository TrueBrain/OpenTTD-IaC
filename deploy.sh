#!/bin/sh

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 [global|production|staging]"
    exit 1
fi

TYPE=${1}

for chart in $(cd ${TYPE} && ls *.yaml); do
    chart=$(echo ${chart} | sed 's/.yaml$//')
    if [ "${chart}" = "global" ]; then continue; fi

    if [ "${TYPE}" = "global" ]; then
        helm dep update charts/${chart}
        helm upgrade --namespace ${TYPE} --install ${TYPE}-${chart} -f ${TYPE}/global.yaml -f ${TYPE}/${chart}.yaml charts/${chart}
    else
        dest=$(mktemp -d)

        app_version=$(cat ${TYPE}/versions.csv | grep "^${chart}:" | cut -d: -f2)
        if [ -z "${app_version}" ]; then
            echo "WARNING: skipping ${chart} as no version to deploy was defined!"
            continue
        fi
        if [ -e charts/${chart}/requirements.yaml ]; then
            helm package -u --app-version ${app_version} charts/${chart} -d ${dest}
        else
            helm package --app-version ${app_version} charts/${chart} -d ${dest}
        fi
        helm upgrade --namespace ${TYPE} --install ${TYPE}-${chart} -f ${TYPE}/global.yaml -f ${TYPE}/${chart}.yaml ${dest}/${chart}*.tgz

        rm -rf ${dest}
    fi
done
