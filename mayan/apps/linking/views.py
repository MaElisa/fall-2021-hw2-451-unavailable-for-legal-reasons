from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    AssignRemoveView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.views import DocumentListView

from .forms import SmartLinkConditionForm, SmartLinkForm
from .icons import icon_smart_link_condition, icon_smart_link_setup
from .links import link_smart_link_condition_create, link_smart_link_create
from .models import ResolvedSmartLink, SmartLink, SmartLinkCondition
from .permissions import (
    permission_smart_link_create, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)

logger = logging.getLogger(__name__)


class ResolvedSmartLinkView(DocumentListView):
    def dispatch(self, request, *args, **kwargs):
        self.document = get_object_or_404(
            klass=Document, pk=self.kwargs['document_id']
        )
        self.smart_link = get_object_or_404(
            klass=SmartLink, pk=self.kwargs['smart_link_id']
        )

        AccessControlList.objects.check_access(
            obj=self.document, permission=permission_document_view,
            user=request.user
        )

        AccessControlList.objects.check_access(
            obj=self.smart_link, permission=permission_smart_link_view,
            user=request.user
        )

        return super(
            ResolvedSmartLinkView, self
        ).dispatch(request, *args, **kwargs)

    def get_document_queryset(self):
        try:
            queryset = self.smart_link.get_linked_document_for(
                document=self.document
            )
        except Exception as exception:
            queryset = Document.objects.none()

            try:
                AccessControlList.objects.check_access(
                    obj=self.smart_link, permission=permission_smart_link_edit,
                    user=self.request.user
                )
            except PermissionDenied:
                pass
            else:
                messages.error(
                    message=_(
                        'Smart link query error: %s' % exception
                    ), request=self.request,
                )

        return queryset

    def get_extra_context(self):
        dynamic_label = self.smart_link.get_dynamic_label(self.document)
        if dynamic_label:
            title = _('Documents in smart link: %s') % dynamic_label
        else:
            title = _(
                'Documents in smart link "%(smart_link)s" as related to '
                '"%(document)s"'
            ) % {
                'document': self.document,
                'smart_link': self.smart_link.label,
            }

        context = super(ResolvedSmartLinkView, self).get_extra_context()
        context.update(
            {
                'object': self.document,
                'title': title,
            }
        )
        return context


class SetupSmartLinkDocumentTypesView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available document types')
    object_permission = permission_smart_link_edit
    right_list_title = _('Document types enabled')

    def add(self, item):
        self.get_object().document_types.add(item)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _(
                'Document type for which to enable smart link: %s'
            ) % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(
            klass=SmartLink, pk=self.kwargs['smart_link_id']
        )

    def left_list(self):
        # TODO: filter document type list by user ACL
        return AssignRemoveView.generate_choices(
            choices=DocumentType.objects.exclude(
                pk__in=self.get_object().document_types.all()
            )
        )

    def remove(self, item):
        self.get_object().document_types.remove(item)

    def right_list(self):
        # TODO: filter document type list by user ACL
        return AssignRemoveView.generate_choices(
            choices=self.get_object().document_types.all()
        )


class SmartLinkListView(SingleObjectListView):
    object_permission = permission_smart_link_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_smart_link_setup,
            'no_results_main_link': link_smart_link_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Indexes group documents into units, usually with similar '
                'properties and of equal or similar types. Smart links '
                'allow defining relationships between documents even '
                'if they are in different indexes and are of different '
                'types.'
            ),
            'no_results_title': _(
                'There are no smart links'
            ),
            'title': _('Smart links'),
        }

    def get_smart_link_queryset(self):
        return SmartLink.objects.all()

    def get_source_queryset(self):
        return self.get_smart_link_queryset()


class DocumentSmartLinkListView(SmartLinkListView):
    def dispatch(self, request, *args, **kwargs):
        self.document = get_object_or_404(
            klass=Document, pk=self.kwargs['document_id']
        )

        AccessControlList.objects.check_access(
            obj=self.document, permission=permission_document_view,
            user=request.user
        )

        return super(
            DocumentSmartLinkListView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'document': self.document,
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_smart_link_setup,
            'no_results_text': _(
                'Smart links allow defining relationships between '
                'documents even if they are in different indexes and '
                'are of different types.'
            ),
            'no_results_title': _(
                'There are no smart links for this document'
            ),
            'object': self.document,
            'title': _('Smart links for document: %s') % self.document,
        }

    def get_smart_link_queryset(self):
        return ResolvedSmartLink.objects.get_for(document=self.document)


class SmartLinkCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create new smart link')}
    form_class = SmartLinkForm
    post_action_redirect = reverse_lazy(viewname='linking:smart_link_list')
    view_permission = permission_smart_link_create


class SmartLinkEditView(SingleObjectEditView):
    form_class = SmartLinkForm
    model = SmartLink
    object_permission = permission_smart_link_edit
    pk_url_kwarg = 'smart_link_id'
    post_action_redirect = reverse_lazy(viewname='linking:smart_link_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit smart link: %s') % self.get_object()
        }


class SmartLinkDeleteView(SingleObjectDeleteView):
    model = SmartLink
    object_permission = permission_smart_link_delete
    pk_url_kwarg = 'smart_link_id'
    post_action_redirect = reverse_lazy(viewname='linking:smart_link_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete smart link: %s') % self.get_object()
        }


class SmartLinkConditionListView(SingleObjectListView):
    view_permission = permission_smart_link_edit

    def get_extra_context(self):
        return {
            'hide_link': True,
            'no_results_icon': icon_smart_link_condition,
            'no_results_main_link': link_smart_link_condition_create.resolve(
                context=RequestContext(
                    request=self.request, dict_={
                        'object': self.get_smart_link()
                    }
                )
            ),
            'no_results_text': _(
                'Conditions are small logic units that when combined '
                'define how the smart link will behave.'
            ),
            'no_results_title': _(
                'There are no conditions for this smart link'
            ),
            'object': self.get_smart_link(),
            'title': _(
                'Conditions for smart link: %s'
            ) % self.get_smart_link(),
        }

    def get_smart_link(self):
        return get_object_or_404(
            klass=SmartLink, pk=self.kwargs['smart_link_id']
        )

    def get_source_queryset(self):
        return self.get_smart_link().conditions.all()


class SmartLinkConditionCreateView(SingleObjectCreateView):
    form_class = SmartLinkConditionForm

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            obj=self.get_smart_link(), permission=permission_smart_link_edit,
            user=request.user
        )

        return super(
            SmartLinkConditionCreateView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'title': _(
                'Add new conditions to smart link: "%s"'
            ) % self.get_smart_link(),
            'object': self.get_smart_link(),
        }

    def get_instance_extra_data(self):
        return {'smart_link': self.get_smart_link()}

    def get_post_action_redirect(self):
        return reverse(
            viewname='linking:smart_link_condition_list',
            kwargs={'smart_link_id': self.get_smart_link().pk}
        )

    def get_queryset(self):
        return self.get_smart_link().conditions.all()

    def get_smart_link(self):
        return get_object_or_404(
            klass=SmartLink, pk=self.kwargs['smart_link_id']
        )


class SmartLinkConditionEditView(SingleObjectEditView):
    form_class = SmartLinkConditionForm
    model = SmartLinkCondition

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            obj=self.get_object().smart_link,
            permission=permission_smart_link_edit, user=request.user
        )

        return super(
            SmartLinkConditionEditView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'condition': self.get_object(),
            'navigation_object_list': ('object', 'condition'),
            'object': self.get_object().smart_link,
            'title': _('Edit smart link condition'),
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='linking:smart_link_condition_list',
            kwargs={'smart_link_id': self.get_object().smart_link.pk}
        )


class SmartLinkConditionDeleteView(SingleObjectDeleteView):
    model = SmartLinkCondition

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            obj=self.get_object().smart_link,
            permission=permission_smart_link_edit, user=request.user
        )

        return super(
            SmartLinkConditionDeleteView, self
        ).dispatch(request, *args, **kwargs)

    def get_extra_context(self):
        return {
            'condition': self.get_object(),
            'navigation_object_list': ('object', 'condition'),
            'object': self.get_object().smart_link,
            'title': _(
                'Delete smart link condition: "%s"?'
            ) % self.get_object(),
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='linking:smart_link_condition_list',
            kwargs={'smart_link_id': self.get_object().smart_link.pk}
        )
