import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cost_report.aws_cost_report_stack import AwsCostReportStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cost_report/aws_cost_report_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCostReportStack(app, "aws-cost-report")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
