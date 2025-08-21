from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import FlowType, FlowStatus, FlowInstance

class FlowTypeModelTest(TestCase):
    def test_create_flow_type(self):
        flow_type = FlowType.objects.create(name="Approval", description="Flow for approvals")
        self.assertEqual(flow_type.name, "Approval")
        self.assertEqual(flow_type.description, "Flow for approvals")

class FlowStatusModelTest(TestCase):
    def setUp(self):
        self.flow_type = FlowType.objects.create(name="Leave Request", description="Flow for leave requests")

    def test_create_flow_status(self):
        status = FlowStatus.objects.create(
            name="Pending",
            description="Waiting for approval",
            type_flow=self.flow_type,
            final=False
        )
        self.assertEqual(status.name, "Pending")
        self.assertEqual(status.description, "Waiting for approval")
        self.assertEqual(status.type_flow, self.flow_type)
        self.assertFalse(status.final)

class FlowInstanceModelTest(TestCase):
    def setUp(self):
        self.user_creator = User.objects.create_user(username='creator', password='pass')
        self.user_recipient = User.objects.create_user(username='recipient', password='pass')
        self.user_updater = User.objects.create_user(username='updater', password='pass')
        self.flow_type = FlowType.objects.create(name="Vacation", description="Vacation request")
        self.status = FlowStatus.objects.create(
            name="In Review",
            description="Under review",
            type_flow=self.flow_type,
            final=False
        )

    def test_create_flow_instance(self):
        instance = FlowInstance.objects.create(
            workflow_type=self.flow_type,
            status=self.status,
            comments="Need 5 days off",
            recipient=self.user_recipient,
            created_by=self.user_creator,
            updated_by=self.user_updater,
        )
        self.assertEqual(instance.workflow_type, self.flow_type)
        self.assertEqual(instance.status, self.status)
        self.assertEqual(instance.comments, "Need 5 days off")
        self.assertEqual(instance.recipient, self.user_recipient)
        self.assertEqual(instance.created_by, self.user_creator)
        self.assertEqual(instance.updated_by, self.user_updater)
        self.assertIsNotNone(instance.created_at)
        self.assertIsNotNone(instance.updated_at)
