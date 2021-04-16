my $string = q|apiVersion: apps/v1
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

if ( $ARGV[0] > 0 ) {
    $string =~ s/REPLICA-COUNT/$ARGV[0]/g;

    open(my $f, '>', 'k8s.yaml');
    print $f $string;
    close $f;
}

else {
    die "failed; please use a positive integer for the number of shards\n";
}
