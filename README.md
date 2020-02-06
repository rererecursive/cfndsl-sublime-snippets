## Description
Auto-completion for CloudFormation templates written in [Cfndsl](https://github.com/cfndsl/cfndsl)

## Example
![](example.gif)

## Generating the files
The snippets are produced from the Cfndsl [resource spec](https://github.com/cfndsl/cfndsl/blob/master/lib/cfndsl/aws/resource_specification.json) using a Docker container:\
`./build.sh && ./run.sh`

The files will then be available in the `snippets` directory.

To use them, copy them to Sublime's config:\
`cp -r snippets /home/$USER/.config/sublime-text-3/Packages/User`
