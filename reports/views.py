from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from reports.models import Report
from reports.serializers import ReportSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_report(request):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(
            {
                'message': 'Report submitted successfully',
                'data' : serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_reports(request):
    reports = Report.objects.filter(user=request.user)
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_detail(request, report_id):
    try:
        report = Report.objects.get(id=report_id, user=request.user)
    except Report.DoesNotExist:
        return Response(
            {'error': 'Report Not Found'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = ReportSerializer(report)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_reports(request):
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def review_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response(
            {'error' : 'Report Not Found'},
            status=status.HTTP_404_NOT_FOUND
        )
    report.review()
    return Response(
        {'message': f'Report {report_id} marked as reviewed'},
        status=status.HTTP_200_OK
    )

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def resolve_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response(
            {'error' : 'Report Not Found'},
            status=status.HTTP_404_NOT_FOUND
        )
    report.resolve()
    return Response(
        {'message': f'Report {report_id} reviewed successfully'},
        status=status.HTTP_200_OK
    )

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def reject_report(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response(
            {'message' : 'Report Not Found'},
            status=status.HTTP_404_NOT_FOUND
        )
    report.reject()
    return Response(
        {'message' : f'Report {report_id} rejected'},
        status=status.HTTP_200_OK
    )

