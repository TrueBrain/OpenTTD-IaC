FROM python:3.6-alpine

RUN pip install flake8

# Run flake8 over the code
COPY deployer deployer
COPY .flake8 .flake8
RUN flake8 deployer


FROM python:3.6-alpine

ARG KUBECTL_VERSION=v1.13.0
ARG HELM_VERSION=v2.12.1

WORKDIR /code

COPY requirements.txt \
        LICENSE \
        README.md \
        .version \
        /code/
COPY run.sh /usr/bin/
COPY charts /code/charts
COPY deployer /code/deployer
COPY config /code/config

RUN apk --no-cache add \
                ca-certificates \
                curl \
        && curl -LOs https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl \
        && curl -s https://storage.googleapis.com/kubernetes-helm/helm-${HELM_VERSION}-linux-amd64.tar.gz | tar xvz \
        && mv kubectl /usr/bin/kubectl \
        && mv linux-amd64/helm /usr/bin/helm \
        && mv linux-amd64/tiller /usr/bin/tiller \
        && chmod +x /usr/bin/kubectl \
        && chmod +x /usr/bin/helm \
        && chmod +x /usr/bin/tiller \
        && helm init --client-only \
        && helm repo remove local \
        && rm -rf linux-amd64 \
        && apk --no-cache del \
                curl

RUN pip install -r requirements.txt

# Validate that what was installed was what was expected
RUN pip freeze 2>/dev/null | grep -v "deployer" > requirements.installed \
        && diff -u requirements.txt requirements.installed 1>&2 \
        || ( echo "!! ERROR !! requirements.txt defined different packages or versions for installation" \
                && exit 1 ) 1>&2

ENTRYPOINT ["run.sh"]
CMD []
