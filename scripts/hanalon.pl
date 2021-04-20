$k8s = q|apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: hanalon-bot
  namespace: hanalon
  annotations:
    seccomp.security.alpha.kubernetes.io/pod: "docker/default"
spec:
  replicas: REPLICA-COUNT
  serviceName: bot
  selector:
    matchLabels:
      hanalon: bot
  template:
    metadata:
      labels:
        hanalon: bot
      annotations:
        seccomp.security.alpha.kubernetes.io/pod: "docker/default"
    spec:
      dnsPolicy: Default
      containers:
        - name: bot
          image: hanalon/bot
          env:
            - name: config
              valueFrom:
                secretKeyRef:
                  name: hanalon-secret
                  key: config
            - name: shard_count
              value: "REPLICA-COUNT"
            - name: pod_name
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
          resources:
            limits:
              memory: "512Mi"
              cpu: "500m"
            requests:
              memory: "128Mi"
              cpu: "125m"
          securityContext:
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            capabilities:
              drop:
                - NET_RAW
                - ALL
      automountServiceAccountToken: false
|;

$config = `base64 -in config.yaml`;
chomp($config);

$container = "hanalon/bot";
$github = "docker.pkg.github.com/sakura-no-hana/hanalon/bot";

if ($ARGV[0] eq "bot") {
    if ($ARGV[1] =~ /^(start|run)$/) {
        if ($ARGV[2] =~ /^(k8s|kubernetes|kube)$/) {
            if (not(`kubectl`)) {
                die "kubectl does not appear to be installed. please install it here: https://kubernetes.io/docs/tasks/tools/\n"
            } else {
                $shards = 1;

                @shard_arg = grep(/^--shards=(?!0)[0-9]+$/, @ARGV[3..$#ARGV]);

                if ($shard_arg[0]) {
                    @shard_arg = split(/=/, $shard_arg[0]);
                    $shards = $shard_arg[-1];
                }

                $k8s =~ s/REPLICA-COUNT/$shards/g;

                open(my $f, '>', 'k8s.yaml');
                print $f $k8s;
                close $f;

                if (grep(/^--rebuild$/, @ARGV[3..$#ARGV])) {
                    `kubectl create namespace hanalon`;
                    `kubectl delete -f k8s.yaml --namespace=hanalon`;
                    `kubectl delete secret hanalon-secret --namespace=hanalon`;
                    `kubectl create secret generic hanalon-secret --namespace=hanalon --from-literal=config=$config`;
                }
                `kubectl apply -f k8s.yaml --namespace=hanalon`;
            }
        }
        elsif($ARGV[2] eq "docker") {
            if (not(`docker 2>&1`)) {
                die "docker does not appear to be installed. please install it here: https://docs.docker.com/get-docker/\n";
            } else {
                if (grep(/^--rebuild$/, @ARGV[3..$#ARGV])) {
                    `docker build -t $container .`;
                }
                `docker stop hanalon-bot`;
                `docker run -d --rm --name hanalon-bot -e config=$config $container`;
            }
        }
        elsif($ARGV[2] = ~/^(py|python)$/) {
            if (not(`git`)) {
                die "git does not appear to be installed. please install it here: https://github.com/git-guides/install-git\n"
            } elsif (not(`python3 -V`)) {
                die "python 3 does not appear to be installed. please install it here: https://www.python.org/downloads/\n"
            } else {
                @req_arg = grep(/^(--req|--requirements|-r)=(pip|poetry)$/, @ARGV[3..$#ARGV]);

                if ($req_arg[0]) {
                    @req_arg = split(/=/, $req_arg[0]);
                    $req = $req_arg[-1];

                    if ($req eq "pip") {
                        `pip3 install -r requirements.txt`;
                    } else {
                        if (not(`poetry`)) {
                            `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`;
                        }
                        `poetry update`;
                        `poetry install`;
                    }
                }

                `nohup python3 src/__main__.py >/dev/null 2>&1 &`;
            }
        }
    } elsif ($ARGV[1] eq "build") {
        if (`docker 2>&1`) {
            `docker build -t $container .`;
            `docker tag $container $github`;
            `docker push $container &`;
            `docker push $github &`;
            `wait`;
        } else {
            die "docker does not appear to be installed. please install it here: https://docs.docker.com/get-docker/\n";
        }
    } elsif ($ARGV[1] eq "kill") {
        if (`docker 2>&1`) {
            `docker stop hanalon-bot 2>&1`;
            `docker rm hanalon-bot 2>&1`;
        }

        if (`kubectl`) {
            `kubectl delete -n hanalon statefulset hanalon-bot 2>&1`;
        }

        `pkill hanalon-bot`;
    } elsif ($ARGV[1] eq "test") {
        if (not(`python3 -V`)) {
            die "python 3 does not appear to be installed. please install it here: https://www.python.org/downloads/\n";
        } else {
            if (not(`pip3 show pytest`)) {
                `pip3 install pytest`;
            }
            if (grep(/^--(cov|coverage)$/, @ARGV[3..$#ARGV])) {
                if (not(`pip3 show pytest-cov`)) {
                    `pip3 install pytest-cov`;
                }
                `pytest --cov=src/utils -v 1>&0`;
            }
            else {
                `pytest -v 1>&0`;
            }
            
        }
    }

} elsif ($ARGV[0] =~ /^(site|website)$/) {
    die "unfortunately, we have not created the website yet. stay tuned.\n";
} elsif ($ARGV[0] =~ /^(mongo|mongodb|db|database)$/) {
    die "we currently use mongodb atlas; there is no local database needed.\n";
}
