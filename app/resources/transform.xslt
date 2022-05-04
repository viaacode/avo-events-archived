<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:mh="https://zeticon.mediahaven.com/metadata/20.3/mh/"
    xmlns:mhs="https://zeticon.mediahaven.com/metadata/20.3/mhs/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <xsl:output method="xml" encoding="UTF-8" byte-order-mark="no" indent="yes"/>
    <xsl:template match="/">
        <mhs:Sidecar xmlns:mhs="https://zeticon.mediahaven.com/metadata/20.3/mhs/"
            xmlns:mh="https://zeticon.mediahaven.com/metadata/20.3/mh/" version="20.3">
            <mhs:Descriptive>
                <xsl:apply-templates select="//mhs:Descriptive/mh:Title"/>
                <xsl:apply-templates select="//mhs:Descriptive/mh:Description"/>
                <xsl:apply-templates select="//mhs:Descriptive/mh:Keywords"/>
            </mhs:Descriptive>
            <xsl:apply-templates select="//mhs:Dynamic"/>
        </mhs:Sidecar>
    </xsl:template>

    <xsl:template match="mhs:Dynamic">
        <xsl:copy>
            <!-- Copy all dynamic data except for s3 metadata, md5, PID, CP metadata and some problematic fields -->
            <xsl:apply-templates select="*[not(self::s3_bucket | self::s3_domain | self::s3_object_owner | self::s3_object_key | self::md5_viaa | self::PID | self::CP | self::CP_id | self::dcterms_issued_index | self::dcterms_created_index)]"/>
            <!-- Add new avo specific tags -->
            <Original_CP>
                <xsl:value-of select="//mhs:Dynamic/CP"/>
            </Original_CP>
            <Original_CP_id>
                <xsl:value-of select="//mhs:Dynamic/CP_id"/>
            </Original_CP_id>
            <dc_relations type="list">
                <is_verwant_aan>
                    <xsl:value-of select="//mhs:Dynamic/PID"/>
                </is_verwant_aan>
                <is_versie_van>
                    <xsl:value-of select="//mhs:Administrative/mh:ExternalId"/>
                </is_versie_van>
            </dc_relations>
        </xsl:copy>
    </xsl:template>

    <!--Identity template copies content forward, needed for a deep copy while adding new elements -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- <xsl:template match="@* | node()" mode="deep-copy-no-namespace">
        <xsl:element name="{name()}">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:element>
    </xsl:template> -->
</xsl:stylesheet>
