from .attachment_admin import AttachmentAdmin
from .biological_evidence_admin import BiologicalEvidenceAdmin
from .evidence_admin import EvidenceAdmin
from .identification_evidence_admin import IdentificationEvidenceAdmin
from .image_admin import ImageAdmin
from .other_evidence_admin import OtherEvidenceAdmin
from .testimony_admin import TestimonyAdmin
from .vehicle_evidence_admin import VehicleEvidenceAdmin

__all__ = [
    "EvidenceAdmin",
    "TestimonyAdmin",
    "AttachmentAdmin",
    "ImageAdmin",
    "BiologicalEvidenceAdmin",
    "IdentificationEvidenceAdmin",
    "VehicleEvidenceAdmin",
    "OtherEvidenceAdmin",
]
