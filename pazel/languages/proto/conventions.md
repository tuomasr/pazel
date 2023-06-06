# Protocol Buffer Conventions

Bazel Build file dependencies generated for Protocol Buffer source files (.proto) follow the [recommended code organization](https://blog.bazel.build/2017/02/27/protocol-buffers.html#recommended-code-organization) from the Bazel team.

To recap here:

1. One `proto_library` rule per `.proto` file.
2. A file named `foo.proto` will be in a rule named `foo_proto`, which is located in the same package.
3. A `<lang>_proto_library` that wraps a `proto_library` named `foo_proto` should be called `foo_<lang>_proto`, and be located in the same package.
