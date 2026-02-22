from rest_framework import serializers
from .models import DetectiveBoard, BoardItem, BoardConnection

# -------------------------
# Detective Board
# -------------------------


class DetectiveBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectiveBoard
        fields = "__all__"
        read_only_fields = ("id", "detective")


# -------------------------
# Board Item
# -------------------------


class BoardItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardItem
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, attrs):
        board = attrs.get("board")
        evidence = attrs.get("evidence")

        # Optional: prevent adding same evidence twice to same board
        if BoardItem.objects.filter(board=board, evidence=evidence).exists():
            raise serializers.ValidationError("This evidence is already on this board.")

        return attrs


# -------------------------
# Board Connection
# -------------------------


class BoardConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardConnection
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, attrs):
        from_item = attrs.get("from_item")
        to_item = attrs.get("to_item")

        if from_item.board != to_item.board:
            raise serializers.ValidationError(
                "Both items must belong to the same board."
            )

        return attrs
